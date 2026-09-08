from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.document import Document
from backend.app.models.user import User
from backend.app.schemas.search import DocumentUploadResponse
from backend.app.services.document_service import (
    list_documents, get_document_by_id, process_uploaded_document
)
from backend.app.api.auth import get_current_active_user, require_engineer

router = APIRouter(prefix="/documents", tags=["Document Intelligence"], dependencies=[Depends(get_current_active_user)])

@router.get("")
def get_documents_list(limit: int = 50, db: Session = Depends(get_db)):
    return list_documents(db, limit=limit)

@router.get("/{document_id}")
def get_document_detail(document_id: str, db: Session = Depends(get_db)):
    doc = get_document_by_id(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.post("/upload", response_model=DocumentUploadResponse)
@router.post("/ingest", response_model=DocumentUploadResponse)
async def upload_document_endpoint(
    file: UploadFile = File(...),
    well_id: Optional[str] = Form("WELL-001"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_engineer)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    return await process_uploaded_document(db, file, well_id=well_id)

