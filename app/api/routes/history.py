from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.domain.models import AnalysisListItem, AnalysisResponse
from app.infra.database.connection import get_db
from app.infra.database.repositories import AnalysisRepository

router = APIRouter()


@router.get(
    "/history",
    response_model=List[AnalysisListItem],
    summary="List analysis history",
    description="Returns a list of all previous resume analyses, ordered by most recent first.",
)
def list_history(db: Session = Depends(get_db)) -> List[AnalysisListItem]:
    repo = AnalysisRepository(db)
    return repo.list_all()


@router.get(
    "/history/{analysis_id}",
    response_model=AnalysisResponse,
    summary="Get a specific analysis",
    description="Returns the full details of a resume analysis by its ID.",
)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)) -> AnalysisResponse:
    repo = AnalysisRepository(db)
    record = repo.get_by_id(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return record
