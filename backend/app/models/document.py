from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from datetime import datetime, timezone
from backend.app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    document_id = Column(String(50), primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), default="PDF") # PDF, TXT, CSV, DOCX
    file_size_bytes = Column(Integer, default=0)
    upload_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    well_id = Column(String(50), nullable=True, index=True)
    total_pages = Column(Integer, default=1)
    processing_status = Column(String(50), default="PROCESSED") # PENDING, PROCESSING, PROCESSED, FAILED
    extracted_events_count = Column(Integer, default=0)
    file_path = Column(String(255), nullable=True)
    is_demo_data = Column(Boolean, default=True)


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    chunk_id = Column(String(50), primary_key=True, index=True)
    document_id = Column(String(50), ForeignKey("documents.document_id"), nullable=False, index=True)
    page_number = Column(Integer, default=1)
    chunk_index = Column(Integer, default=0)
    content = Column(Text, nullable=False)
    embedding_json = Column(Text, nullable=True) # Serialized float vector
    metadata_json = Column(Text, nullable=True)


class ExtractedEntity(Base):
    __tablename__ = "extracted_entities"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String(50), ForeignKey("documents.document_id"), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False) # WELL, FORMATION, DEPTH, EVENT_TYPE, CAUSE, MITIGATION, SEVERITY
    entity_value = Column(String(255), nullable=False)
    confidence = Column(Float, default=0.9)
    page_number = Column(Integer, default=1)
