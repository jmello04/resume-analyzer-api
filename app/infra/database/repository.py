"""Implementação concreta do repositório de análises de currículos."""

from typing import Any, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.domain.interfaces import AnalysisRepositoryInterface
from app.infra.database.models import AnalysisRecord


class AnalysisRepository(AnalysisRepositoryInterface):
    """Repositório SQLAlchemy para persistência e consulta de análises de currículos.

    Args:
        db: Sessão ativa do banco de dados fornecida via injeção de dependência.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, filename: str, resume_text: str, result: dict[str, Any]) -> AnalysisRecord:
        """Persiste uma nova análise de currículo no banco de dados.

        Args:
            filename: Nome original do arquivo PDF enviado.
            resume_text: Texto extraído do currículo.
            result: Dicionário com os campos avaliados (score, level, listas de pontos).

        Returns:
            O registro de análise recém-criado e atualizado com o ID gerado.
        """
        new_record = AnalysisRecord(
            filename=filename,
            resume_text=resume_text,
            score=result["score"],
            level=result["level"],
            strong_points=result["strong_points"],
            weak_points=result["weak_points"],
            suggestions=result["suggestions"],
            detected_skills=result["detected_skills"],
        )
        self.db.add(new_record)
        self.db.commit()
        self.db.refresh(new_record)
        return new_record

    def get_by_id(self, analysis_id: int) -> Optional[AnalysisRecord]:
        """Busca um registro de análise pelo seu identificador único.

        Args:
            analysis_id: ID do registro a ser buscado.

        Returns:
            O registro correspondente, ou None se não encontrado.
        """
        return (
            self.db.query(AnalysisRecord)
            .filter(AnalysisRecord.id == analysis_id)
            .first()
        )

    def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> Tuple[List[AnalysisRecord], int]:
        """Recupera todos os registros de análise com suporte a paginação.

        Args:
            skip: Número de registros a ignorar (offset).
            limit: Número máximo de registros a retornar.

        Returns:
            Tupla com a lista de registros paginada e o total absoluto de registros.
        """
        total = self.db.query(AnalysisRecord).count()
        paginated_records = (
            self.db.query(AnalysisRecord)
            .order_by(AnalysisRecord.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return paginated_records, total
