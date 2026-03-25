from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.domain.interfaces import AnalysisRepositoryInterface
from app.infra.database.models import AnalysisRecord


class AnalysisRepository(AnalysisRepositoryInterface):

    def __init__(self, db: Session):
        self.db = db

    def create(self, filename: str, resume_text: str, result: dict) -> AnalysisRecord:
        record = AnalysisRecord(
            filename=filename,
            resume_text=resume_text,
            score=result["score"],
            level=result["level"],
            strong_points=result["strong_points"],
            weak_points=result["weak_points"],
            suggestions=result["suggestions"],
            detected_skills=result["detected_skills"],
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_by_id(self, analysis_id: int) -> Optional[AnalysisRecord]:
        return (
            self.db.query(AnalysisRecord)
            .filter(AnalysisRecord.id == analysis_id)
            .first()
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> Tuple[List[AnalysisRecord], int]:
        total = self.db.query(AnalysisRecord).count()
        items = (
            self.db.query(AnalysisRecord)
            .order_by(AnalysisRecord.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return items, total
