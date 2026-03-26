"""Exceções HTTP customizadas utilizadas em toda a aplicação."""

from fastapi import HTTPException, status


class PDFExtractionError(HTTPException):
    """Erro lançado quando a extração de texto de um arquivo PDF falha.

    Args:
        detail: Mensagem descritiva do motivo da falha na extração.
    """

    def __init__(self, detail: str = "Erro ao extrair texto do PDF") -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class AnalysisProcessingError(HTTPException):
    """Erro lançado quando o processamento ou a análise do currículo falha.

    Args:
        detail: Mensagem descritiva do motivo da falha no processamento.
    """

    def __init__(self, detail: str = "Erro ao processar a análise do currículo") -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class AnalysisNotFoundError(HTTPException):
    """Erro lançado quando uma análise solicitada não é encontrada no banco de dados.

    Args:
        analysis_id: Identificador único da análise que não foi encontrada.
    """

    def __init__(self, analysis_id: int) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Análise com ID {analysis_id} não encontrada",
        )
