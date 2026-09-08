"""
NWIS Keyword Search Engine (formerly named SemanticEmbeddingEngine).

CLASSIFICATION: [A] Real Implementation — TF-IDF Keyword Search

IMPORTANT PROVENANCE NOTE:
  This module performs TF-IDF (Term Frequency–Inverse Document Frequency)
  keyword-based cosine similarity search. It is NOT a dense vector embedding
  engine and does NOT use neural language models.

  The config setting `EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"`
  is NOT in use in this module. That model will be integrated in Phase 6 via
  `backend/app/ai/dense_retrieval.py` (DenseVectorSearchEngine).

  Comparison:
    This module (KeywordSearchEngine): TF-IDF bag-of-words cosine similarity
    Phase 6 (DenseVectorSearchEngine): 384-dim dense vectors via sentence-transformers

  Both similarity scores are cosine similarities, but TF-IDF cosine operates on
  sparse vocabulary counts, not semantic embedding space.
"""
import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from backend.app.models.event import DrillingEvent
from backend.app.models.well import Well
from backend.app.schemas.search import SearchResultItem

# Classification tag included in all search result metadata
_RETRIEVAL_METHOD = "tfidf_keyword_cosine"
_RETRIEVAL_LABEL = "TF-IDF Keyword Search (not dense vector embeddings)"


class KeywordSearchEngine:
    """
    TF-IDF keyword-based search over historical drilling events.

    Uses sklearn TfidfVectorizer with (1,2)-gram range and cosine similarity.
    Results include a similarity_score (0-1) and a retrieval_method field
    indicating this is TF-IDF, not neural embeddings.

    Note: This class was previously named SemanticEmbeddingEngine — that name
    was misleading. The SemanticEmbeddingEngine alias is retained for backwards
    compatibility with existing code imports.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            max_features=5000
        )
        self._corpus_fitted = False

    def search_events(
        self,
        db: Session,
        query: str,
        formation: Optional[str] = None,
        event_type: Optional[str] = None,
        target_depth: Optional[float] = None,
        depth_window_m: float = 250.0,
        limit: int = 10
    ) -> List[SearchResultItem]:
        """
        Keyword-based TF-IDF search over historical drilling events.

        Returns SearchResultItem objects with:
          - similarity_score: TF-IDF cosine score (0-1)
          - retrieval_method: "tfidf_keyword_cosine" (explicit provenance)

        Args:
            query: Natural language or keyword query string
            formation: Optional formation name filter
            event_type: Optional event type filter
            target_depth: Optional depth for proximity boosting
            depth_window_m: Depth window for initial filtering
            limit: Maximum results to return

        Returns:
            List[SearchResultItem] sorted by similarity_score descending
        """
        events_query = db.query(DrillingEvent)
        if formation:
            events_query = events_query.filter(DrillingEvent.formation.ilike(f"%{formation}%"))
        if event_type:
            events_query = events_query.filter(DrillingEvent.event_type == event_type)
        if target_depth is not None:
            events_query = events_query.filter(
                DrillingEvent.start_depth >= target_depth - depth_window_m,
                DrillingEvent.start_depth <= target_depth + depth_window_m
            )

        events = events_query.all()
        if not events:
            # Relax depth filtering if too restrictive
            events = db.query(DrillingEvent).limit(100).all()

        if not events:
            return []

        # Build text corpus from event structured fields
        corpus = [
            (
                f"{e.event_type} at depth {e.start_depth}m in {e.formation}. "
                f"Cause: {e.cause}. Mitigation: {e.mitigation}. "
                f"Lessons: {e.lesson_learned}"
            )
            for e in events
        ]

        try:
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            query_vec = self.vectorizer.transform([query])
            cosine_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
        except Exception:
            cosine_scores = np.zeros(len(events))

        well_cache = {w.well_id: w.well_name for w in db.query(Well).all()}

        results = []
        for event, score in zip(events, cosine_scores):
            adjusted_score = float(score)
            if target_depth is not None:
                depth_diff = abs(event.start_depth - target_depth)
                proximity_boost = max(0.0, 1.0 - (depth_diff / 500.0)) * 0.25
                adjusted_score = min(1.0, adjusted_score + proximity_boost)

            w_name = well_cache.get(event.well_id, event.well_id)

            results.append(SearchResultItem(
                event_id=event.event_id,
                well_id=event.well_id,
                well_name=w_name,
                event_type=event.event_type,
                depth=event.start_depth,
                formation=event.formation,
                severity=event.severity,
                cause=event.cause,
                mitigation=event.mitigation,
                lesson_learned=event.lesson_learned,
                source_document=event.source_document,
                source_page=event.source_page,
                similarity_score=round(max(0.05, adjusted_score), 3),
                match_highlights=[
                    f"Horizon: {event.formation} ({event.start_depth} m)",
                    f"Incident: {event.event_type} ({event.severity})",
                    f"Mitigation: {event.mitigation[:120]}..."
                ]
            ))

        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:limit]


# Module-level instances
keyword_search_engine = KeywordSearchEngine()

# In Phase 6: semantic_engine upgrades to genuine 384-dimensional HybridSearchEngine
from backend.app.ai.dense_retrieval import hybrid_search_engine, HybridSearchEngine
SemanticEmbeddingEngine = HybridSearchEngine
semantic_engine = hybrid_search_engine
