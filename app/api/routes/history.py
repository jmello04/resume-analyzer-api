"""Endpoints para consulta do histórico de análises de currículos."""

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
    limit: int = Query(
        default=100, ge=1, le=500, description="Número máximo de registros a retornar"
    ),
    db: Session = Depends(get_db),
) -> HistoryListResponse:
    """Lista o histórico de análises com suporte a paginação.

    Args:
        skip: Offset de registros para paginação.
        limit: Limite de registros por página (máximo 500).
        db: Sessão ativa do banco de dados (injetada via dependência).

    Returns:
        Objeto com o total de análises e a lista paginada de registros.
    """
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
    """Recupera uma análise específica pelo seu identificador.

    Args:
        analysis_id: Identificador único da análise.
        db: Sessão ativa do banco de dados (injetada via dependência).

    Returns:
        Registro completo da análise correspondente ao ID.

    Raises:
        HTTPException 404: Se a análise com o ID informado não existir.
    """
    return get_analysis_by_id(db, analysis_id)
