from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    score: int = Field(..., ge=0, le=100)
    level: str
    strong_points: List[str]
    weak_points: List[str]
    suggestions: List[str]
    detected_skills: List[str]


class AnalysisResponse(AnalysisResult):
    id: int
    filename: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisListItem(BaseModel):
    id: int
    filename: str
    score: int
    level: str
    created_at: datetime

    model_config = {"from_attributes": True}
