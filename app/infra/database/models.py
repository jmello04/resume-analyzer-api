from sqlalchemy import Column, DateTime, Integer, JSON, String, Text
from sqlalchemy.sql import func

from app.infra.database.connection import Base


class AnalysisRecord(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    resume_text = Column(Text, nullable=False)
    score = Column(Integer, nullable=False)
    level = Column(String(50), nullable=False)
    strong_points = Column(JSON, nullable=False, default=lambda: [])
    weak_points = Column(JSON, nullable=False, default=lambda: [])
    suggestions = Column(JSON, nullable=False, default=lambda: [])
    detected_skills = Column(JSON, nullable=False, default=lambda: [])
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
