from typing import List, Tuple

from sqlalchemy.orm import Session

from app.core.exceptions import AnalysisNotFoundError
from app.infra.database.models import AnalysisRecord
from app.infra.database.repository import AnalysisRepository


def get_all_analyses(db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[AnalysisRecord], int]:
    repo = AnalysisRepository(db)
    return repo.get_all(skip=skip, limit=limit)


def get_analysis_by_id(db: Session, analysis_id: int) -> AnalysisRecord:
    repo = AnalysisRepository(db)
    record = repo.get_by_id(analysis_id)
    if not record:
        raise AnalysisNotFoundError(analysis_id)
    return record
