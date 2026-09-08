from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class KeywordSearchRequest(BaseModel):
    query: str
    formation: Optional[str] = None
    event_type: Optional[str] = None
    min_depth: Optional[float] = None
    max_depth: Optional[float] = None
    limit: int = 20

class SemanticSearchRequest(BaseModel):
    query: str
    formation: Optional[str] = None
    event_type: Optional[str] = None
    target_depth: Optional[float] = None
    depth_window_m: Optional[float] = 200.0
    limit: int = 10
    retrieval_mode: Optional[str] = "hybrid"  # "hybrid" | "dense" | "sparse"
    alpha: Optional[float] = 0.65  # Dense vs sparse weighting in hybrid mode

class SearchResultItem(BaseModel):
    event_id: str
    well_id: str
    well_name: str
    event_type: str
    depth: float
    formation: str
    severity: str
    cause: str
    mitigation: str
    lesson_learned: str
    source_document: str
    source_page: int
    # Blended or individual similarity score (0.0 - 1.0)
    similarity_score: float
    dense_score: Optional[float] = None
    sparse_score: Optional[float] = None
    retrieval_method: Optional[str] = "hybrid_dense_sparse"
    match_highlights: List[str] = []

class AssistantQueryRequest(BaseModel):
    question: str
    active_well_id: Optional[str] = None
    current_depth: Optional[float] = None
    current_formation: Optional[str] = None
    provider: Optional[str] = "auto"  # "auto" | "offline" | "gemini" | "openai"

class AssistantQueryResponse(BaseModel):
    question: str
    answer: str
    grounded_evidence: List[SearchResultItem]
    is_fallback_response: bool = False
    model_used: str = "NWIS Offline Structured Evidence Retrieval (Hybrid Dense/Sparse)"
    retrieval_method: str = "hybrid_dense_sparse"
    provider_used: str = "offline"
    is_offline_mode: bool = True
    citations: List[Dict[str, Any]] = []
    timestamp: str

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    file_type: str
    file_size_bytes: int
    total_pages: int
    extracted_events_count: int
    extracted_events: List[dict]
    processing_status: str
    # Extraction quality summary — added in Phase 0 for provenance transparency
    extraction_quality_report: Optional[dict] = None
    tables_extracted: Optional[List[dict]] = None
    provenance: Optional[dict] = None

class UnifiedSearchRequest(BaseModel):
    query: str
    well_id: Optional[str] = "WELL-001"
    depth: Optional[float] = None
    formation: Optional[str] = None
    conversation_id: Optional[str] = None
    event_type: Optional[str] = None
    min_depth: Optional[float] = None
    max_depth: Optional[float] = None
    limit: Optional[int] = 5

class UnifiedSearchSourceItem(BaseModel):
    document: str
    well: str
    depth: str
    formation: Optional[str] = None
    event: Optional[str] = None
    relevance: Optional[float] = None

class UnifiedSearchResponse(BaseModel):
    answer: str
    confidence: Optional[float] = None
    answer_type: str = "historical_evidence"  # "historical_evidence" | "general_knowledge" | "insufficient_evidence"
    sources: List[UnifiedSearchSourceItem] = []
    context: Dict[str, Any] = {}
    warnings: List[str] = []
    follow_up_questions: List[str] = []
    conversation_id: str
    timestamp: str

