from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.domain.schemas import AnalysisResponse, HistoryListResponse
from app.infra.database.connection import get_db
from app.services.history_service import get_all_analyses, get_analysis_by_id

router = APIRouter()


@router.get(
    "/history",
    response_model=HistoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar histórico de análises",
    description=(
        "Retorna todas as análises de currículos realizadas anteriormente, "
        "ordenadas da mais recente para a mais antiga. "
        "Suporta paginação via parâmetros `skip` e `limit`."
    ),
)
def list_history(
    skip: int = Query(default=0, ge=0, description="Número de registros a ignorar (paginação)"),
    limit: int = Query(default=100, ge=1, le=500, description="Número máximo de registros a retornar"),
    db: Session = Depends(get_db),
) -> HistoryListResponse:
    analyses, total = get_all_analyses(db, skip=skip, limit=limit)
    return HistoryListResponse(total=total, analyses=analyses)


@router.get(
    "/history/{analysis_id}",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Buscar análise por ID",
    description="Retorna os detalhes completos de uma análise específica identificada pelo seu ID único.",
)
def get_history_by_id(
    analysis_id: int,
    db: Session = Depends(get_db),
) -> AnalysisResponse:
    return get_analysis_by_id(db, analysis_id)
