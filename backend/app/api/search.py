from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.search import (
    KeywordSearchRequest, SemanticSearchRequest, SearchResultItem,
    AssistantQueryRequest, AssistantQueryResponse,
    UnifiedSearchRequest, UnifiedSearchResponse
)
from backend.app.services.search_service import (
    perform_keyword_search, perform_semantic_search, query_rag_assistant,
    perform_unified_search, get_dynamic_suggestions
)
from backend.app.services.conversation_service import list_search_history
from backend.app.api.auth import require_geologist

router = APIRouter(prefix="/search", tags=["Search & Assistant"])

@router.post("", response_model=UnifiedSearchResponse)
def unified_search_endpoint(req: UnifiedSearchRequest, db: Session = Depends(get_db)):
    """
    Primary NWIS Search & Grounded Assistant Endpoint.
    Orchestrates Hybrid Retrieval (vector similarity + structured filtering),
    conversation memory, and the LLM Service (Gemini API / Grounded Engine).
    """
    return perform_unified_search(db, req)

@router.get("/history")
def get_search_history_endpoint(limit: int = Query(20, description="Max history items")):
    """Returns conversation and search session history."""
    return list_search_history(limit=limit)

@router.get("/suggestions")
def get_search_suggestions_endpoint(
    well_id: Optional[str] = Query(None),
    depth: Optional[float] = Query(None),
    formation: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Returns dynamic, context-aware prompt suggestions based on current well horizons."""
    return get_dynamic_suggestions(db, well_id=well_id, depth=depth, formation=formation)

@router.post("/keyword", response_model=List[SearchResultItem])
def keyword_search_endpoint(req: KeywordSearchRequest, db: Session = Depends(get_db)):
    return perform_keyword_search(db, req)

@router.post("/semantic", response_model=List[SearchResultItem])
def semantic_search_endpoint(req: SemanticSearchRequest, db: Session = Depends(get_db)):
    return perform_semantic_search(db, req)

@router.post("/assistant", response_model=AssistantQueryResponse)
def assistant_query_endpoint(req: AssistantQueryRequest, db: Session = Depends(get_db)):
    return query_rag_assistant(db, req)

