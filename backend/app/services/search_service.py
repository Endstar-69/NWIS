from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.event import DrillingEvent
from backend.app.models.well import Well
from backend.app.schemas.search import (
    KeywordSearchRequest, SemanticSearchRequest, SearchResultItem,
    AssistantQueryRequest, AssistantQueryResponse
)
from backend.app.ai.embeddings import semantic_engine
from backend.app.ai.rag_assistant import rag_assistant

def perform_keyword_search(db: Session, req: KeywordSearchRequest) -> List[SearchResultItem]:
    query = db.query(DrillingEvent)
    
    if req.formation:
        query = query.filter(DrillingEvent.formation.ilike(f"%{req.formation}%"))
    if req.event_type:
        query = query.filter(DrillingEvent.event_type == req.event_type)
    if req.min_depth is not None:
        query = query.filter(DrillingEvent.start_depth >= req.min_depth)
    if req.max_depth is not None:
        query = query.filter(DrillingEvent.start_depth <= req.max_depth)

    q_term = req.query.strip().lower()
    if q_term:
        words = [w for w in q_term.split() if len(w) > 2]
        if words:
            for w in words:
                query = query.filter(
                    (DrillingEvent.cause.ilike(f"%{w}%")) |
                    (DrillingEvent.mitigation.ilike(f"%{w}%")) |
                    (DrillingEvent.lesson_learned.ilike(f"%{w}%")) |
                    (DrillingEvent.event_type.ilike(f"%{w}%")) |
                    (DrillingEvent.formation.ilike(f"%{w}%"))
                )
        else:
            query = query.filter(
                (DrillingEvent.cause.ilike(f"%{q_term}%")) |
                (DrillingEvent.mitigation.ilike(f"%{q_term}%")) |
                (DrillingEvent.event_type.ilike(f"%{q_term}%"))
            )

    events = query.limit(req.limit).all()
    well_cache = {w.well_id: w.well_name for w in db.query(Well).all()}

    results = []
    for e in events:
        results.append(SearchResultItem(
            event_id=e.event_id,
            well_id=e.well_id,
            well_name=well_cache.get(e.well_id, e.well_id),
            event_type=e.event_type,
            depth=e.start_depth,
            formation=e.formation,
            severity=e.severity,
            cause=e.cause,
            mitigation=e.mitigation,
            lesson_learned=e.lesson_learned,
            source_document=e.source_document,
            source_page=e.source_page,
            similarity_score=1.0,
            match_highlights=[f"Match found in {e.event_type} at {e.start_depth} m ({e.formation})"]
        ))
    return results

def perform_semantic_search(db: Session, req: SemanticSearchRequest) -> List[SearchResultItem]:
    return semantic_engine.search_events(
        db=db,
        query=req.query,
        formation=req.formation,
        event_type=req.event_type,
        target_depth=req.target_depth,
        depth_window_m=req.depth_window_m or 250.0,
        limit=req.limit,
        retrieval_mode=getattr(req, "retrieval_mode", "hybrid") or "hybrid",
        alpha=getattr(req, "alpha", 0.65)
    )

def query_rag_assistant(db: Session, req: AssistantQueryRequest) -> AssistantQueryResponse:
    return rag_assistant.answer_query(
        db=db,
        question=req.question,
        active_well_id=req.active_well_id,
        current_depth=req.current_depth or 3420.0,
        current_formation=req.current_formation or "Barail Sandstone",
        provider=getattr(req, "provider", "auto") or "auto"
    )

import re
from datetime import datetime, timezone
from backend.app.schemas.search import (
    UnifiedSearchRequest, UnifiedSearchResponse, UnifiedSearchSourceItem
)
from backend.app.services.llm_service import llm_service
from backend.app.services.conversation_service import (
    create_conversation_id, get_conversation_history, append_conversation_turn
)
from backend.app.ai.dense_retrieval import hybrid_search_engine

def perform_unified_search(db: Session, req: UnifiedSearchRequest) -> UnifiedSearchResponse:
    """
    Executes unified hybrid retrieval and routes to LLM service with full conversation memory.
    """
    conversation_id = req.conversation_id or create_conversation_id()
    well_id = req.well_id or "WELL-001"
    depth = req.depth or 3420.0
    formation = req.formation or "Barail Sandstone"

    # 1. Smart Query Concept Extraction (Hybrid Search Filtering)
    q_lower = req.query.lower()

    # Extract depth from query if present e.g. "around 3668 m" or "at 3600-3700 m"
    detected_depth = depth
    depth_match = re.search(r'(?:around|at|depth of|near)\s*(\d{3,4}(?:\.\d+)?)', q_lower)
    if depth_match:
        try:
            detected_depth = float(depth_match.group(1))
        except ValueError:
            pass

    # Extract formation from query if mentioned
    detected_formation = formation
    for f_name in ["Barail", "Barail Sandstone", "Tipam", "Tipam Sandstone", "Kopili", "Girujan", "Disang", "Bokabil"]:
        if f_name.lower() in q_lower:
            detected_formation = f_name
            break

    # Extract event type if mentioned
    detected_event_type = req.event_type
    if not detected_event_type:
        if any(w in q_lower for w in ["mud loss", "lost circulation", "lcm"]):
            detected_event_type = "MUD_LOSS"
        elif any(w in q_lower for w in ["stuck pipe", "differential sticking", "pipe sticking", "packoff"]):
            detected_event_type = "STUCK_PIPE"
        elif any(w in q_lower for w in ["gas kick", "kick", "well control", "influx", "blowout"]):
            detected_event_type = "GAS_KICK"

    # 2. Hybrid Search Retrieval (Vector Similarity + Structured Metadata)
    retrieved_items = hybrid_search_engine.search_events(
        db=db,
        query=req.query,
        formation=detected_formation if any(k in q_lower for k in ["this formation", "current formation", "horizon", "barail", "tipam", "kopili"]) else None,
        target_depth=detected_depth,
        depth_window_m=300.0,
        limit=req.limit or 5,
        retrieval_mode="hybrid"
    )

    # Secondary fallback to broaden if event type was detected but results are sparse
    if detected_event_type and len(retrieved_items) < 2:
        additional = db.query(DrillingEvent).filter(
            DrillingEvent.event_type.ilike(f"%{detected_event_type.replace('_', ' ')}%")
        ).limit(3).all()
        well_names = {w.well_id: w.well_name for w in db.query(Well).all()}
        for e in additional:
            if not any(it.event_id == e.event_id for it in retrieved_items):
                retrieved_items.append(SearchResultItem(
                    event_id=e.event_id,
                    well_id=e.well_id,
                    well_name=well_names.get(e.well_id, e.well_id),
                    event_type=e.event_type,
                    depth=e.start_depth,
                    formation=e.formation,
                    severity=e.severity,
                    cause=e.cause,
                    mitigation=e.mitigation,
                    lesson_learned=e.lesson_learned,
                    source_document=e.source_document,
                    source_page=e.source_page,
                    similarity_score=0.85,
                    match_highlights=[f"Structured match for {e.event_type} in {e.formation}"]
                ))

    # 3. Fetch past conversation turns for bounded context
    past_turns = get_conversation_history(conversation_id)
    conversation_history = []
    for turn in past_turns:
        conversation_history.append({"role": "user", "content": turn["query"]})
        conversation_history.append({"role": "assistant", "content": turn["answer"]})

    # 4. Invoke LLM Service
    llm_context = {
        "well": well_id,
        "depth": detected_depth,
        "formation": detected_formation
    }
    llm_res = llm_service.generate_answer(
        query=req.query,
        retrieved_evidence=retrieved_items,
        context=llm_context,
        conversation_history=conversation_history
    )

    # 5. Build structured response & format sources
    formatted_sources = []
    for s in llm_res.get("sources", []):
        formatted_sources.append(UnifiedSearchSourceItem(
            document=s.get("document", "Daily Drilling Report"),
            well=s.get("well", "Offset Well"),
            depth=str(s.get("depth", "")),
            formation=s.get("formation"),
            event=s.get("event"),
            relevance=s.get("relevance")
        ))

    # 6. Record turn in conversation session
    append_conversation_turn(
        conversation_id=conversation_id,
        query=req.query,
        response=llm_res,
        well_id=well_id,
        depth=detected_depth,
        formation=detected_formation
    )

    now_str = datetime.now(timezone.utc).isoformat()
    return UnifiedSearchResponse(
        answer=llm_res.get("answer", ""),
        confidence=llm_res.get("confidence"),
        answer_type=llm_res.get("answer_type", "historical_evidence"),
        sources=formatted_sources,
        context=llm_res.get("context", llm_context),
        warnings=llm_res.get("warnings", []),
        follow_up_questions=llm_res.get("follow_up_questions", []),
        conversation_id=conversation_id,
        timestamp=now_str
    )

def get_dynamic_suggestions(db: Session, well_id: Optional[str] = None, depth: Optional[float] = None, formation: Optional[str] = None) -> List[str]:
    """
    Generates dynamic prompt suggestions based on actual active well conditions and offset hazards.
    """
    d = depth or 3600.0
    f = formation or "Barail Sandstone"

    # Query offset events in this formation or near this depth
    sample_events = db.query(DrillingEvent).filter(
        (DrillingEvent.formation.ilike(f"%{f.split()[0]}%")) |
        (DrillingEvent.start_depth.between(d - 300, d + 300))
    ).limit(3).all()

    suggestions = [
        f"What happened in nearby wells around {d:.0f} m in {f}?",
    ]
    if sample_events:
        top_ev = sample_events[0]
        suggestions.append(f"Which offset wells experienced {top_ev.event_type.lower()} in {top_ev.formation}?")
        suggestions.append(f"Show previous {top_ev.event_type.lower()} mitigations around {top_ev.start_depth:.0f} m.")
    else:
        suggestions.append(f"Which offset wells experienced mud losses in {f}?")
        suggestions.append(f"Show previous differential sticking incidents and mitigations.")

    suggestions.append(f"What are the historical gas kick warning signs in {f}?")
    return suggestions[:4]

