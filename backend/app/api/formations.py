from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.formation import Formation
from backend.app.schemas.well import FormationSchema
from backend.app.api.auth import get_current_active_user

router = APIRouter(prefix="/formations", tags=["Formations"])

@router.get("", response_model=List[FormationSchema])
def list_formations(db: Session = Depends(get_db)):
    return db.query(Formation).order_by(Formation.typical_top_depth.asc()).all()

@router.get("/{formation_id}", response_model=FormationSchema)
def get_formation(formation_id: str, db: Session = Depends(get_db)):
    fmt = db.query(Formation).filter(Formation.formation_id == formation_id).first()
    if not fmt:
        raise HTTPException(status_code=404, detail=f"Formation '{formation_id}' not found")
    return fmt
