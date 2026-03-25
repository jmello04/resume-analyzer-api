from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Pontuação geral do currículo de 0 a 100")
    level: str = Field(..., description="Nível profissional detectado: Júnior, Pleno ou Sênior")
    strong_points: List[str] = Field(..., description="Pontos fortes identificados no currículo")
    weak_points: List[str] = Field(..., description="Pontos fracos identificados no currículo")
    suggestions: List[str] = Field(..., description="Sugestões de melhoria para o currículo")
    detected_skills: List[str] = Field(..., description="Habilidades técnicas detectadas")


class AnalysisResponse(BaseModel):
    id: int = Field(..., description="Identificador único da análise")
    filename: str = Field(..., description="Nome do arquivo analisado")
    score: int = Field(..., ge=0, le=100, description="Pontuação geral do currículo de 0 a 100")
    level: str = Field(..., description="Nível profissional detectado: Júnior, Pleno ou Sênior")
    strong_points: List[str] = Field(..., description="Pontos fortes identificados no currículo")
    weak_points: List[str] = Field(..., description="Pontos fracos identificados no currículo")
    suggestions: List[str] = Field(..., description="Sugestões de melhoria para o currículo")
    detected_skills: List[str] = Field(..., description="Habilidades técnicas detectadas")
    created_at: datetime = Field(..., description="Data e hora em que a análise foi realizada")

    model_config = {"from_attributes": True}


class HistoryListResponse(BaseModel):
    total: int = Field(..., description="Total de análises registradas")
    analyses: List[AnalysisResponse] = Field(..., description="Lista de análises realizadas")
