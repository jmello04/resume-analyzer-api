"""Casos de uso relacionados ao histórico de análises de currículos."""

from typing import List, Tuple

from sqlalchemy.orm import Session

from app.core.exceptions import AnalysisNotFoundError
from app.infra.database.models import AnalysisRecord
from app.infra.database.repository import AnalysisRepository


def get_all_analyses(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[List[AnalysisRecord], int]:
    """Recupera todas as análises registradas com suporte a paginação.

    Args:
        db: Sessão ativa do banco de dados.
        skip: Quantidade de registros a ignorar (offset).
        limit: Número máximo de registros a retornar.

    Returns:
        Tupla contendo a lista de registros e o total absoluto de análises.
    """
    repo = AnalysisRepository(db)
    return repo.get_all(skip=skip, limit=limit)


def get_analysis_by_id(db: Session, analysis_id: int) -> AnalysisRecord:
    """Recupera uma análise específica pelo seu identificador único.

    Args:
        db: Sessão ativa do banco de dados.
        analysis_id: Identificador único da análise.

    Returns:
        O registro de análise correspondente ao ID informado.

    Raises:
        AnalysisNotFoundError: Se nenhum registro for encontrado com o ID fornecido.
    """
    repo = AnalysisRepository(db)
    record = repo.get_by_id(analysis_id)
    if not record:
        raise AnalysisNotFoundError(analysis_id)
    return record
