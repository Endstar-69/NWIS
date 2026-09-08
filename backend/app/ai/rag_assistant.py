"""
NWIS Pluggable Retrieval-Augmented Generation (RAG) Assistant.

CLASSIFICATION:
  - [A] Real Implementation — Offline Structured Evidence Retrieval (Always Available)
  - [D] Optional Enterprise Integration — Online Generative RAG (Gemini / OpenAI)

PROVENANCE NOTE:
  - Offline Mode: 100% deterministic, assembled directly from retrieved offset-well
    database records and dense vector matches. Zero external dependencies.
  - Online Mode: Dynamically enabled when GEMINI_API_KEY or OPENAI_API_KEY is configured.
    Grounds external LLM queries strictly in retrieved offset records, enforcing
    well names, depths, formations, and source document citations.
  - Automatic Fallback: If external API keys are missing, network is unavailable,
    or API calls fail, the assistant gracefully falls back to Offline Structured
    Retrieval, transparently documenting the fallback reason.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import httpx
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.ai.dense_retrieval import hybrid_search_engine
from backend.app.schemas.search import AssistantQueryResponse, SearchResultItem

_MIN_EVIDENCE_SCORE = 0.12


class BaseRAGProvider(ABC):
    """Abstract base class for all NWIS RAG generative and retrieval providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

    @property
    @abstractmethod
    def is_offline(self) -> bool:
        pass

    @abstractmethod
    def generate_response(
        self,
        question: str,
        retrieved_evidence: List[SearchResultItem],
        active_well_id: Optional[str] = "WELL-001",
        current_depth: Optional[float] = None,
        current_formation: Optional[str] = None
    ) -> AssistantQueryResponse:
        """Generates an answer grounded strictly in the provided evidence items."""
        pass


class OfflineStructuredRetrievalProvider(BaseRAGProvider):
    """
    [A] Real Implementation — Deterministic Evidence Structuring Provider.

    Operates entirely offline without external language models. Formats retrieved
    evidence into a structured engineering briefing with root causes, recorded
    mitigations, and source citations.
    """

    @property
    def provider_name(self) -> str:
        return "offline"

    @property
    def model_name(self) -> str:
        return "NWIS Offline Structured Evidence Retrieval (Hybrid Dense/Sparse)"

    @property
    def is_offline(self) -> bool:
        return True

    def generate_response(
        self,
        question: str,
        retrieved_evidence: List[SearchResultItem],
        active_well_id: Optional[str] = "WELL-001",
        current_depth: Optional[float] = None,
        current_formation: Optional[str] = None,
        fallback_notice: Optional[str] = None
    ) -> AssistantQueryResponse:
        now_str = datetime.now(timezone.utc).isoformat()

        # Build citations list
        citations = [
            {
                "well_name": item.well_name,
                "well_id": item.well_id,
                "depth_m": item.depth,
                "formation": item.formation,
                "event_type": item.event_type,
                "severity": item.severity,
                "source_document": item.source_document,
                "source_page": item.source_page,
                "similarity_score": item.similarity_score
            }
            for item in retrieved_evidence
        ]

        # Strict evidence guard
        if not retrieved_evidence or retrieved_evidence[0].similarity_score < _MIN_EVIDENCE_SCORE:
            refusal_text = (
                "No sufficiently supported historical evidence was found in the "
                "offset well knowledge repository for this query (similarity score below "
                f"calibrated threshold {_MIN_EVIDENCE_SCORE:.2f}).\n\n"
                "The NWIS platform strictly refuses to fabricate responses when empirical "
                "offset data is absent. Please refine your query parameters or consult field "
                "mud logs directly."
            )
            return AssistantQueryResponse(
                question=question,
                answer=refusal_text,
                grounded_evidence=[],
                is_fallback_response=True,
                model_used=self.model_name,
                retrieval_method="hybrid_dense_sparse",
                provider_used=self.provider_name,
                is_offline_mode=True,
                citations=[],
                timestamp=now_str
            )

        top_item = retrieved_evidence[0]
        depth_ctx = f"near {current_depth:.1f} m" if current_depth else "across offset horizons"
        form_ctx = f"in **{current_formation}**" if current_formation else ""

        evidence_lines = []
        for item in retrieved_evidence[:4]:
            evidence_lines.append(
                f"- **{item.well_name}** at **{item.depth:.1f} m** ({item.formation}): "
                f"Encountered **{item.event_type}** (Severity: {item.severity}).\n"
                f"  *Cause*: {item.cause}\n"
                f"  *Mitigation*: {item.mitigation}\n"
                f"  *(Citation: `{item.source_document}`, p. {item.source_page} | Score: {item.similarity_score:.2f})*"
            )

        evidence_text = "\n".join(evidence_lines)

        fallback_prefix = f"> ⚠️ **Note**: {fallback_notice}\n\n" if fallback_notice else ""

        answer = (
            f"{fallback_prefix}"
            f"### Historical Offset Evidence & Well Control Advisory\n"
            f"Analysis of offset well events {depth_ctx} {form_ctx}:\n\n"
            f"{evidence_text}\n\n"
            f"### Primary Operational Lessons Learned\n"
            f"- **Dominant Hazard**: {top_item.event_type} (Severity: {top_item.severity})\n"
            f"- **Root Cause Summary**: {top_item.cause}\n"
            f"- **Demonstrated Mitigation**: {top_item.mitigation}\n"
            f"- **Key Takeaway**: {top_item.lesson_learned}\n\n"
            f"> *Provenance: Assembled deterministically from validated offset well logs via "
            f"hybrid 384-dim dense vector and sparse keyword matching. Zero generative fabrication.*"
        )

        return AssistantQueryResponse(
            question=question,
            answer=answer,
            grounded_evidence=retrieved_evidence[:4],
            is_fallback_response=bool(fallback_notice),
            model_used=self.model_name,
            retrieval_method="hybrid_dense_sparse",
            provider_used=self.provider_name,
            is_offline_mode=True,
            citations=citations[:4],
            timestamp=now_str
        )


class GeminiRAGProvider(BaseRAGProvider):
    """
    [D] Optional Enterprise Integration — Google Gemini Grounded Generative RAG.

    Calls Google Gemini REST API using httpx when GEMINI_API_KEY is configured.
    Enforces strict grounding on retrieved evidence records. Falls back to
    OfflineStructuredRetrievalProvider if unconfigured or on error.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model
        self.offline_fallback = OfflineStructuredRetrievalProvider()

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return f"google/{self.model}"

    @property
    def is_offline(self) -> bool:
        return False

    def generate_response(
        self,
        question: str,
        retrieved_evidence: List[SearchResultItem],
        active_well_id: Optional[str] = "WELL-001",
        current_depth: Optional[float] = None,
        current_formation: Optional[str] = None
    ) -> AssistantQueryResponse:
        if not self.api_key:
            return self.offline_fallback.generate_response(
                question=question,
                retrieved_evidence=retrieved_evidence,
                active_well_id=active_well_id,
                current_depth=current_depth,
                current_formation=current_formation,
                fallback_notice="GEMINI_API_KEY not configured. Switched automatically to offline structured retrieval."
            )

        if not retrieved_evidence or retrieved_evidence[0].similarity_score < _MIN_EVIDENCE_SCORE:
            return self.offline_fallback.generate_response(
                question=question,
                retrieved_evidence=retrieved_evidence,
                active_well_id=active_well_id,
                current_depth=current_depth,
                current_formation=current_formation
            )

        # Format grounding evidence context
        evidence_snippets = []
        for i, item in enumerate(retrieved_evidence[:5], 1):
            evidence_snippets.append(
                f"[Evidence #{i}]\n"
                f"Well: {item.well_name} ({item.well_id})\n"
                f"Depth: {item.depth:.1f} m | Formation: {item.formation}\n"
                f"Event: {item.event_type} | Severity: {item.severity}\n"
                f"Cause: {item.cause}\n"
                f"Mitigation: {item.mitigation}\n"
                f"Lesson Learned: {item.lesson_learned}\n"
                f"Source: {item.source_document}, Page: {item.source_page}\n"
                f"Similarity: {item.similarity_score:.2f}\n"
            )
        grounding_context = "\n".join(evidence_snippets)

        system_instruction = (
            "You are the NWIS Senior Petroleum Operations and Well-Control Advisor. "
            "Your role is to assist drillers and petroleum engineers with actionable, "
            "empirically grounded recommendations based STRICTLY on historical offset-well data.\n"
            "RULES:\n"
            "1. Rely solely on the provided historical evidence. Do NOT invent facts or hallucinate.\n"
            "2. Cite specific well names, depths, and source documents for every operational claim.\n"
            "3. Provide concrete mitigations and root cause lessons for the active operation.\n"
            "4. Maintain a professional, technical drilling engineering tone."
        )

        user_content = (
            f"ACTIVE DRILLING CONTEXT:\n"
            f"Active Well: {active_well_id}, Current Depth: {current_depth or 'Unknown'} m, "
            f"Current Formation: {current_formation or 'Unknown'}\n\n"
            f"GROUND TRUTH EVIDENCE FROM OFFSET WELLS:\n{grounding_context}\n\n"
            f"ENGINEER QUERY:\n{question}\n\n"
            f"Please synthesize a rigorous operational response referencing the cited offset records."
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{system_instruction}\n\n{user_content}"}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1024
            }
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        content_parts = candidates[0].get("content", {}).get("parts", [])
                        if content_parts:
                            generated_text = content_parts[0].get("text", "")
                            citations = [
                                {
                                    "well_name": item.well_name,
                                    "well_id": item.well_id,
                                    "depth_m": item.depth,
                                    "formation": item.formation,
                                    "event_type": item.event_type,
                                    "severity": item.severity,
                                    "source_document": item.source_document,
                                    "source_page": item.source_page,
                                    "similarity_score": item.similarity_score
                                }
                                for item in retrieved_evidence[:4]
                            ]
                            return AssistantQueryResponse(
                                question=question,
                                answer=generated_text,
                                grounded_evidence=retrieved_evidence[:4],
                                is_fallback_response=False,
                                model_used=self.model_name,
                                retrieval_method="hybrid_dense_sparse",
                                provider_used=self.provider_name,
                                is_offline_mode=False,
                                citations=citations,
                                timestamp=datetime.now(timezone.utc).isoformat()
                            )
                # If API returned non-200, fallback
                error_detail = f"Gemini API returned HTTP {resp.status_code}: {resp.text[:120]}"
        except Exception as e:
            error_detail = f"Gemini API request failed: {str(e)[:120]}"

        # Graceful fallback to offline
        return self.offline_fallback.generate_response(
            question=question,
            retrieved_evidence=retrieved_evidence,
            active_well_id=active_well_id,
            current_depth=current_depth,
            current_formation=current_formation,
            fallback_notice=f"{error_detail}. Switched automatically to offline structured retrieval."
        )


class OpenAIRAGProvider(BaseRAGProvider):
    """
    [D] Optional Enterprise Integration — OpenAI Grounded Generative RAG.

    Calls OpenAI Chat Completions API using httpx when OPENAI_API_KEY is configured.
    Falls back to OfflineStructuredRetrievalProvider on error or missing key.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model
        self.offline_fallback = OfflineStructuredRetrievalProvider()

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return f"openai/{self.model}"

    @property
    def is_offline(self) -> bool:
        return False

    def generate_response(
        self,
        question: str,
        retrieved_evidence: List[SearchResultItem],
        active_well_id: Optional[str] = "WELL-001",
        current_depth: Optional[float] = None,
        current_formation: Optional[str] = None
    ) -> AssistantQueryResponse:
        if not self.api_key:
            return self.offline_fallback.generate_response(
                question=question,
                retrieved_evidence=retrieved_evidence,
                active_well_id=active_well_id,
                current_depth=current_depth,
                current_formation=current_formation,
                fallback_notice="OPENAI_API_KEY not configured. Switched automatically to offline structured retrieval."
            )

        if not retrieved_evidence or retrieved_evidence[0].similarity_score < _MIN_EVIDENCE_SCORE:
            return self.offline_fallback.generate_response(
                question=question,
                retrieved_evidence=retrieved_evidence,
                active_well_id=active_well_id,
                current_depth=current_depth,
                current_formation=current_formation
            )

        evidence_snippets = []
        for i, item in enumerate(retrieved_evidence[:5], 1):
            evidence_snippets.append(
                f"[Evidence #{i}] Well: {item.well_name} ({item.well_id}) | Depth: {item.depth:.1f} m | "
                f"Formation: {item.formation} | Event: {item.event_type} | Cause: {item.cause} | "
                f"Mitigation: {item.mitigation} | Lesson: {item.lesson_learned} | "
                f"Source: {item.source_document} p.{item.source_page}"
            )
        grounding_context = "\n".join(evidence_snippets)

        system_prompt = (
            "You are the NWIS Petroleum Well Operations Advisor. Ground all answers strictly in the "
            "provided historical offset well evidence. Always cite specific wells, depths, and source documents. "
            "Never fabricate facts."
        )

        user_prompt = (
            f"Active Well: {active_well_id}, Current Depth: {current_depth or 'Unknown'} m, "
            f"Current Formation: {current_formation or 'Unknown'}\n\n"
            f"Retrieved Historical Records:\n{grounding_context}\n\n"
            f"Question: {question}"
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1024
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        answer_text = choices[0].get("message", {}).get("content", "")
                        citations = [
                            {
                                "well_name": item.well_name,
                                "well_id": item.well_id,
                                "depth_m": item.depth,
                                "formation": item.formation,
                                "event_type": item.event_type,
                                "severity": item.severity,
                                "source_document": item.source_document,
                                "source_page": item.source_page,
                                "similarity_score": item.similarity_score
                            }
                            for item in retrieved_evidence[:4]
                        ]
                        return AssistantQueryResponse(
                            question=question,
                            answer=answer_text,
                            grounded_evidence=retrieved_evidence[:4],
                            is_fallback_response=False,
                            model_used=self.model_name,
                            retrieval_method="hybrid_dense_sparse",
                            provider_used=self.provider_name,
                            is_offline_mode=False,
                            citations=citations,
                            timestamp=datetime.now(timezone.utc).isoformat()
                        )
                error_detail = f"OpenAI API returned HTTP {resp.status_code}: {resp.text[:120]}"
        except Exception as e:
            error_detail = f"OpenAI API request failed: {str(e)[:120]}"

        return self.offline_fallback.generate_response(
            question=question,
            retrieved_evidence=retrieved_evidence,
            active_well_id=active_well_id,
            current_depth=current_depth,
            current_formation=current_formation,
            fallback_notice=f"{error_detail}. Switched automatically to offline structured retrieval."
        )


class PluggableRAGAssistant:
    """
    Pluggable RAG Assistant managing provider routing, dense retrieval, and generation.
    """

    def __init__(self):
        self.offline_provider = OfflineStructuredRetrievalProvider()
        self.gemini_provider = GeminiRAGProvider()
        self.openai_provider = OpenAIRAGProvider()

    def get_provider(self, requested: Optional[str] = "auto") -> BaseRAGProvider:
        """Resolves the active RAG provider based on configuration and request."""
        req = (requested or "auto").lower().strip()
        if req == "gemini":
            return self.gemini_provider
        if req == "openai":
            return self.openai_provider
        if req == "offline":
            return self.offline_provider

        # Auto resolution
        if settings.GEMINI_API_KEY:
            return self.gemini_provider
        if settings.OPENAI_API_KEY:
            return self.openai_provider
        return self.offline_provider

    def answer_query(
        self,
        db: Session,
        question: str,
        active_well_id: Optional[str] = "WELL-001",
        current_depth: Optional[float] = None,
        current_formation: Optional[str] = None,
        provider: Optional[str] = "auto"
    ) -> AssistantQueryResponse:
        """
        Executes hybrid dense vector retrieval and routes to active RAG provider.
        """
        # Contextual formation filtering
        formation_filter = None
        if current_formation and any(
            kw in question.lower()
            for kw in ["this formation", "current formation", "this horizon", "barail", "tipam"]
        ):
            formation_filter = current_formation

        # 1. Retrieve evidence via Hybrid Dense/Sparse Search Engine
        retrieved_items = hybrid_search_engine.search_events(
            db=db,
            query=question,
            formation=formation_filter,
            target_depth=current_depth,
            limit=5,
            retrieval_mode="hybrid"
        )

        # 2. Select provider and generate grounded response
        selected_provider = self.get_provider(provider)
        return selected_provider.generate_response(
            question=question,
            retrieved_evidence=retrieved_items,
            active_well_id=active_well_id,
            current_depth=current_depth,
            current_formation=current_formation
        )


# Global singleton instance
pluggable_rag_assistant = PluggableRAGAssistant()

# Backwards compatibility aliases
OfflineEvidenceAssistant = OfflineStructuredRetrievalProvider
RAGAssistant = PluggableRAGAssistant
rag_assistant = pluggable_rag_assistant
