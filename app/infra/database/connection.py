from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ResumeAnalysisORM(Base):
    __tablename__ = "resume_analyses"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    raw_text = Column(Text, nullable=False)
    score = Column(Integer, nullable=False)
    level = Column(String(50), nullable=False)
    strong_points = Column(JSON, nullable=False)
    weak_points = Column(JSON, nullable=False)
    suggestions = Column(JSON, nullable=False)
    detected_skills = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
