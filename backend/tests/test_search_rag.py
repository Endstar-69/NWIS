import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.ai.dense_retrieval import (
    dense_embedder, DenseVectorStore, HybridSearchEngine, hybrid_search_engine
)
from backend.app.ai.rag_assistant import (
    pluggable_rag_assistant,
    OfflineStructuredRetrievalProvider,
    GeminiRAGProvider,
    OpenAIRAGProvider
)
from backend.app.schemas.search import (
    SearchResultItem, SemanticSearchRequest, AssistantQueryRequest
)
from backend.app.core.security import create_access_token

from backend.app.core.database import SessionLocal

client = TestClient(app)

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================================================================
# 1. DENSE VECTOR EMBEDDER UNIT TESTS
# =========================================================================

def test_dense_vector_embedding_shape_and_norm():
    texts = [
        "Lost circulation observed at 3450m in Barail Sandstone.",
        "Stuck pipe due to mechanical pack-off while back-reaming.",
        "Gas kick influx detected with 15 bbl pit gain."
    ]
    vecs = dense_embedder.encode(texts)
    assert isinstance(vecs, np.ndarray)
    assert vecs.shape == (3, 384)
    assert vecs.dtype == np.float32

    # Verify L2 unit normalization
    for i in range(3):
        norm = float(np.linalg.norm(vecs[i]))
        assert abs(norm - 1.0) < 1e-4, f"Vector {i} norm is {norm}, expected ~1.0"


def test_dense_vector_cosine_symmetry_and_semantics():
    t1 = "Severe mud loss into fractured formation"
    t2 = "Total lost circulation in fractured carbonate"
    t3 = "Routine bit change and rig maintenance operations"

    v1 = dense_embedder.encode([t1])[0]
    v2 = dense_embedder.encode([t2])[0]
    v3 = dense_embedder.encode([t3])[0]

    sim_1_2 = float(np.dot(v1, v2))
    sim_2_1 = float(np.dot(v2, v1))
    sim_1_3 = float(np.dot(v1, v3))

    # Cosine symmetry
    assert abs(sim_1_2 - sim_2_1) < 1e-6
    # Semantically related drilling hazards should score higher than routine maintenance
    assert sim_1_2 > sim_1_3, f"Expected {sim_1_2} > {sim_1_3}"


# =========================================================================
# 2. DENSE VECTOR STORE UNIT TESTS
# =========================================================================

def test_dense_vector_store_indexing_and_search(tmp_path):
    store = DenseVectorStore(dim=384)
    assert len(store.ids) == 0

    texts = [
        "Lost circulation in Barail Sandstone",
        "Differential pipe sticking in Kopili Shale",
        "Gas influx in Tipam Formation"
    ]
    vecs = dense_embedder.encode(texts)
    ids = ["EVT-1", "EVT-2", "EVT-3"]
    metas = [
        {"event_id": "EVT-1", "formation": "Barail Sandstone", "depth": 3400.0, "event_type": "Lost Circulation"},
        {"event_id": "EVT-2", "formation": "Kopili Shale", "depth": 2800.0, "event_type": "Stuck Pipe"},
        {"event_id": "EVT-3", "formation": "Tipam Formation", "depth": 1900.0, "event_type": "Gas Kick"},
    ]

    store.add_batch(ids, vecs, metas)
    assert len(store.ids) == 3

    # Query matching Barail loss
    q_vec = dense_embedder.encode(["Mud loss in Barail Sandstone"])[0]
    results = store.search(q_vec, top_k=2)
    assert len(results) == 2
    top_meta, top_score = results[0]
    assert top_meta["event_id"] == "EVT-1"
    assert 0.0 <= top_score <= 1.0

    # Test filtering by formation
    kopili_results = store.search(q_vec, top_k=5, formation="Kopili")
    assert len(kopili_results) == 1
    assert kopili_results[0][0]["event_id"] == "EVT-2"

    # Test serialization save and load
    cache_path = str(tmp_path / "test_store.joblib")
    store.save(cache_path)

    loaded_store = DenseVectorStore(dim=384)
    loaded = loaded_store.load(cache_path)
    assert loaded is True
    assert len(loaded_store.ids) == 3
    assert loaded_store.metadata[0]["event_id"] == "EVT-1"


# =========================================================================
# 3. HYBRID SEARCH ENGINE SCORING & WEIGHTING
# =========================================================================

def test_hybrid_search_modes(db_session):
    engine = HybridSearchEngine(alpha=0.65)
    indexed_count = engine.index_events_from_db(db_session, force=True)
    assert indexed_count > 0

    query = "lost circulation mud loss in sandstone"

    # Hybrid mode
    hybrid_res = engine.search_events(
        db=db_session,
        query=query,
        limit=5,
        retrieval_mode="hybrid",
        alpha=0.70
    )
    assert len(hybrid_res) > 0
    top_hybrid = hybrid_res[0]
    assert top_hybrid.retrieval_method == "hybrid_dense_sparse"
    assert top_hybrid.dense_score is not None
    assert top_hybrid.sparse_score is not None
    assert 0.0 <= top_hybrid.similarity_score <= 1.0

    # Pure dense mode
    dense_res = engine.search_events(
        db=db_session,
        query=query,
        limit=5,
        retrieval_mode="dense"
    )
    assert len(dense_res) > 0
    assert dense_res[0].retrieval_method == "dense_vector_cosine"

    # Pure sparse mode
    sparse_res = engine.search_events(
        db=db_session,
        query=query,
        limit=5,
        retrieval_mode="sparse"
    )
    assert len(sparse_res) > 0
    assert sparse_res[0].retrieval_method == "tfidf_keyword_cosine"


def test_hybrid_search_depth_proximity_boost(db_session):
    engine = HybridSearchEngine(alpha=0.50)
    engine.index_events_from_db(db_session)

    # Search with target depth vs without target depth
    res_with_depth = engine.search_events(
        db=db_session,
        query="mud loss",
        target_depth=3400.0,
        limit=10
    )
    assert len(res_with_depth) > 0
    # Results near 3400m should receive proximity boost
    top_item = res_with_depth[0]
    assert 0.0 < top_item.similarity_score <= 1.0


# =========================================================================
# 4. PLUGGABLE RAG ASSISTANT & PROVIDERS
# =========================================================================

def test_offline_structured_retrieval_provider():
    provider = OfflineStructuredRetrievalProvider()
    assert provider.is_offline is True
    assert provider.provider_name == "offline"

    # Test evidence grounding
    evidence = [
        SearchResultItem(
            event_id="EVT-001",
            well_id="WELL-002",
            well_name="Nahorkatiya-14",
            event_type="Lost Circulation",
            depth=3420.0,
            formation="Barail Sandstone",
            severity="HIGH",
            cause="Fracture opening under hydrostatic overbalance",
            mitigation="Pumped 40 bbl coarse LCM pill and lowered mud weight",
            lesson_learned="Pre-treat active system with medium LCM prior to penetrating Barail",
            source_document="DDR_Nahorkatiya_14.pdf",
            source_page=12,
            similarity_score=0.88,
            dense_score=0.90,
            sparse_score=0.84,
            match_highlights=["Barail Sandstone at 3420m"]
        )
    ]

    resp = provider.generate_response(
        question="How do we mitigate lost circulation in Barail Sandstone?",
        retrieved_evidence=evidence,
        current_depth=3400.0,
        current_formation="Barail Sandstone"
    )

    assert resp.is_fallback_response is False
    assert resp.is_offline_mode is True
    assert resp.provider_used == "offline"
    assert "Nahorkatiya-14" in resp.answer
    assert "LCM pill" in resp.answer
    assert len(resp.citations) == 1
    assert resp.citations[0]["source_document"] == "DDR_Nahorkatiya_14.pdf"


def test_offline_structured_retrieval_refusal_when_low_evidence():
    provider = OfflineStructuredRetrievalProvider()
    low_evidence = [
        SearchResultItem(
            event_id="EVT-099",
            well_id="WELL-005",
            well_name="Khoraghat-03",
            event_type="Minor Vibration",
            depth=1200.0,
            formation="Alluvium",
            severity="LOW",
            cause="Unbalanced drill collars",
            mitigation="Adjusted rotary speed",
            lesson_learned="Monitor surface vibration sensors",
            source_document="DDR_Khoraghat_03.pdf",
            source_page=2,
            similarity_score=0.08,  # Below _MIN_EVIDENCE_SCORE (0.12)
            match_highlights=[]
        )
    ]

    resp = provider.generate_response(
        question="What is the nuclear reactor status?",
        retrieved_evidence=low_evidence
    )
    assert resp.is_fallback_response is True
    assert "refuses to fabricate" in resp.answer
    assert len(resp.grounded_evidence) == 0


def test_gemini_provider_unconfigured_fallback():
    provider = GeminiRAGProvider(api_key="")
    evidence = [
        SearchResultItem(
            event_id="EVT-001",
            well_id="WELL-002",
            well_name="Nahorkatiya-14",
            event_type="Lost Circulation",
            depth=3420.0,
            formation="Barail Sandstone",
            severity="HIGH",
            cause="High permeability thief zone",
            mitigation="Pumped LCM",
            lesson_learned="Pre-treat system",
            source_document="DDR.pdf",
            source_page=1,
            similarity_score=0.85
        )
    ]

    resp = provider.generate_response(
        question="What happened in Barail?",
        retrieved_evidence=evidence
    )
    # Since API key is blank, should gracefully fall back to offline
    assert resp.provider_used == "offline"
    assert resp.is_offline_mode is True
    assert "GEMINI_API_KEY not configured" in resp.answer


def test_gemini_provider_with_mocked_success():
    provider = GeminiRAGProvider(api_key="test_fake_gemini_key")
    evidence = [
        SearchResultItem(
            event_id="EVT-001",
            well_id="WELL-002",
            well_name="Nahorkatiya-14",
            event_type="Lost Circulation",
            depth=3420.0,
            formation="Barail Sandstone",
            severity="HIGH",
            cause="Thief zone",
            mitigation="Pumped 50 bbl LCM pill",
            lesson_learned="Monitor pit levels closely",
            source_document="DDR_14.pdf",
            source_page=5,
            similarity_score=0.92
        )
    ]

    mock_gemini_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": (
                                "Based on offset well Nahorkatiya-14 at 3420 m (Barail Sandstone), "
                                "a severe Lost Circulation incident occurred. The crew pumped a 50 bbl "
                                "LCM pill to regain returns (Source: DDR_14.pdf, p. 5)."
                            )
                        }
                    ]
                }
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_gemini_response

    with patch("httpx.Client.post", return_value=mock_resp):
        resp = provider.generate_response(
            question="Mitigation for Barail loss?",
            retrieved_evidence=evidence
        )
        assert resp.is_offline_mode is False
        assert resp.provider_used == "gemini"
        assert "Nahorkatiya-14" in resp.answer
        assert len(resp.citations) == 1


def test_openai_provider_with_mocked_success():
    provider = OpenAIRAGProvider(api_key="test_fake_openai_key")
    evidence = [
        SearchResultItem(
            event_id="EVT-003",
            well_id="WELL-004",
            well_name="Moran-07",
            event_type="Gas Kick",
            depth=3100.0,
            formation="Tipam Sandstone",
            severity="CRITICAL",
            cause="Underbalanced drilling into gas cap",
            mitigation="Shut in well using annular preventer and circulated out via Driller Method",
            lesson_learned="Perform flow checks before and after bit trips",
            source_document="DDR_Moran_07.pdf",
            source_page=8,
            similarity_score=0.89
        )
    ]

    mock_openai_response = {
        "choices": [
            {
                "message": {
                    "content": (
                        "Operational Advisory: Moran-07 encountered a critical Gas Kick at 3100 m in Tipam Sandstone. "
                        "The well was shut in with the annular preventer and killed via the Driller Method (DDR_Moran_07.pdf, p.8)."
                    )
                }
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_openai_response

    with patch("httpx.Client.post", return_value=mock_resp):
        resp = provider.generate_response(
            question="How was the Tipam gas kick handled?",
            retrieved_evidence=evidence
        )
        assert resp.is_offline_mode is False
        assert resp.provider_used == "openai"
        assert "Moran-07" in resp.answer
        assert len(resp.citations) == 1


# =========================================================================
# 5. ENDPOINT INTEGRATION & RBAC TESTS
# =========================================================================

def test_semantic_search_endpoint_hybrid_options(geologist_headers):
    payload = {
        "query": "lost circulation and mud seepage in fractured sandstone",
        "target_depth": 3400.0,
        "retrieval_mode": "hybrid",
        "alpha": 0.65,
        "limit": 5
    }
    resp = client.post("/api/search/semantic", json=payload, headers=geologist_headers)
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    if len(items) > 0:
        top = items[0]
        assert "dense_score" in top
        assert "sparse_score" in top
        assert "similarity_score" in top
        assert top["retrieval_method"] == "hybrid_dense_sparse"


def test_assistant_query_endpoint_offline_mode(geologist_headers):
    payload = {
        "question": "What offset incidents occurred in Barail Sandstone near 3400m?",
        "current_depth": 3400.0,
        "current_formation": "Barail Sandstone",
        "provider": "offline"
    }
    resp = client.post("/api/search/assistant", json=payload, headers=geologist_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider_used"] == "offline"
    assert data["is_offline_mode"] is True
    assert "grounded_evidence" in data
    assert "citations" in data


def test_search_rbac_access_control(viewer_headers):
    # Viewer should be forbidden (403) from search routes
    resp_viewer = client.post("/api/search/semantic", json={"query": "mud loss"}, headers=viewer_headers)
    assert resp_viewer.status_code == 403

    # Unauthenticated should receive 401
    resp_no_auth = client.post("/api/search/semantic", json={"query": "mud loss"})
    assert resp_no_auth.status_code == 401
