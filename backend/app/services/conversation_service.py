"""
NWIS Conversation and Search History Service.

Maintains multi-turn conversation sessions with bounded memory.
Allows engineers to ask follow-up questions while retaining drilling context.
"""

from datetime import datetime, timezone
import uuid
from typing import List, Dict, Any, Optional

# In-memory session store (can also be persisted to SQLite)
_CONVERSATION_STORE: Dict[str, List[Dict[str, Any]]] = {}
_SEARCH_HISTORY: List[Dict[str, Any]] = []


def create_conversation_id() -> str:
    """Generates a unique conversation ID."""
    return f"conv-{uuid.uuid4().hex[:10]}"


def get_conversation_history(conversation_id: str) -> List[Dict[str, Any]]:
    """Retrieves conversation turns for a given ID."""
    return _CONVERSATION_STORE.get(conversation_id, [])


def append_conversation_turn(
    conversation_id: str,
    query: str,
    response: Dict[str, Any],
    well_id: Optional[str] = None,
    depth: Optional[float] = None,
    formation: Optional[str] = None
) -> None:
    """Appends a user query and assistant response turn to the conversation."""
    now_str = datetime.now(timezone.utc).isoformat()

    if conversation_id not in _CONVERSATION_STORE:
        _CONVERSATION_STORE[conversation_id] = []

    turn = {
        "timestamp": now_str,
        "query": query,
        "answer": response.get("answer", ""),
        "answer_type": response.get("answer_type", "historical_evidence"),
        "confidence": response.get("confidence"),
        "sources": response.get("sources", []),
        "follow_up_questions": response.get("follow_up_questions", []),
        "context": {
            "well_id": well_id,
            "depth": depth,
            "formation": formation
        }
    }
    _CONVERSATION_STORE[conversation_id].append(turn)

    # Append to global search history (capped at 100 items)
    _SEARCH_HISTORY.insert(0, {
        "id": f"hist-{uuid.uuid4().hex[:8]}",
        "conversation_id": conversation_id,
        "query": query,
        "timestamp": now_str,
        "well_id": well_id,
        "depth": depth,
        "formation": formation,
        "answer_preview": (response.get("answer", "")[:120] + "...") if len(response.get("answer", "")) > 120 else response.get("answer", ""),
        "sources_count": len(response.get("sources", []))
    })
    if len(_SEARCH_HISTORY) > 100:
        _SEARCH_HISTORY.pop()


def list_search_history(limit: int = 20) -> List[Dict[str, Any]]:
    """Returns the most recent search history records."""
    return _SEARCH_HISTORY[:limit]
