#!/usr/bin/env python3
"""
NWIS Document Ingestion Script
==============================
Processes drilling reports from `documents/sample_reports/`, extracts structured
events and entities, and saves them to the database.

Usage:
    python scripts/ingest_documents.py
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.core.database import SessionLocal
from backend.app.models import Document, DocumentChunk, ExtractedEntity, DrillingEvent, Well
from backend.app.ai.extractor import extractor

REPORTS_DIR = BASE_DIR / "documents" / "sample_reports"

def ingest_all_reports():
    print("=" * 60)
    print(" NWIS Document Ingestion & Knowledge Extraction Pipeline")
    print("=" * 60)

    db = SessionLocal()
    try:
        report_files = list(REPORTS_DIR.glob("*.txt")) + list(REPORTS_DIR.glob("*.pdf"))
        print(f"[INFO] Found {len(report_files)} report files to process in {REPORTS_DIR}")

        for file_path in report_files:
            fname = file_path.name
            doc_id = f"DOC-{file_path.stem}"
            print(f"\n[INFO] Processing: {fname}...")

            pages = extractor.extract_text_from_file(file_path)
            extracted_events = extractor.extract_structured_events(pages, fname)

            # Check if document already exists
            existing_doc = db.query(Document).filter(Document.document_id == doc_id).first()
            if not existing_doc:
                doc_obj = Document(
                    document_id=doc_id,
                    filename=fname,
                    file_type=file_path.suffix.upper().replace(".", ""),
                    file_size_bytes=file_path.stat().st_size,
                    upload_date=datetime.now(timezone.utc),
                    total_pages=len(pages),
                    processing_status="PROCESSED",
                    extracted_events_count=len(extracted_events),
                    file_path=str(file_path),
                    is_demo_data=True
                )
                db.add(doc_obj)
                db.commit()

                # Add chunks
                for page in pages:
                    chunk_id = f"CHK-{doc_id}-{page['page_number']}"
                    chunk_obj = DocumentChunk(
                        chunk_id=chunk_id,
                        document_id=doc_id,
                        page_number=page["page_number"],
                        chunk_index=page["page_number"],
                        content=page["text"],
                        metadata_json=json.dumps({"filename": fname, "page": page["page_number"]})
                    )
                    db.add(chunk_obj)
                db.commit()

            # Save extracted events to DrillingEvent repository if not present
            for idx, ev in enumerate(extracted_events):
                evt_id = f"EVT-EXT-{doc_id}-{idx+1}"
                if not db.query(DrillingEvent).filter(DrillingEvent.event_id == evt_id).first():
                    # Resolve well_id if matching well name exists
                    w_match = db.query(Well).filter(Well.well_name.ilike(f"%{ev['well_name']}%")).first()
                    w_id = w_match.well_id if w_match else "WELL-001"

                    new_event = DrillingEvent(
                        event_id=evt_id,
                        well_id=w_id,
                        event_type=ev["event_type"],
                        start_depth=ev["start_depth"],
                        end_depth=ev["end_depth"],
                        formation=ev["formation"],
                        severity=ev["severity"],
                        cause=ev["cause"],
                        impact=ev["impact"],
                        mitigation=ev["mitigation"],
                        lesson_learned=ev["lesson_learned"],
                        npt_hours=18.0,
                        source_document=fname,
                        source_page=ev["source_page"],
                        confidence=ev["confidence"],
                        is_demo_data=True
                    )
                    db.add(new_event)

                    # Also save extracted entities
                    db.add(ExtractedEntity(
                        document_id=doc_id,
                        entity_type="EVENT_TYPE",
                        entity_value=ev["event_type"],
                        confidence=ev["confidence"],
                        page_number=ev["source_page"]
                    ))
                    db.add(ExtractedEntity(
                        document_id=doc_id,
                        entity_type="FORMATION",
                        entity_value=ev["formation"],
                        confidence=ev["confidence"],
                        page_number=ev["source_page"]
                    ))
                    db.add(ExtractedEntity(
                        document_id=doc_id,
                        entity_type="DEPTH",
                        entity_value=str(ev["start_depth"]),
                        confidence=ev["confidence"],
                        page_number=ev["source_page"]
                    ))

            db.commit()
            print(f"   [SUCCESS] Extracted {len(extracted_events)} structured events from {fname} (Confidence: {extracted_events[0]['confidence'] if extracted_events else 0.9})")

        print("\n" + "=" * 60)
        print("[SUCCESS] All sample reports successfully ingested into Knowledge Repository!")
        print("=" * 60)
    finally:
        db.close()

if __name__ == "__main__":
    ingest_all_reports()
