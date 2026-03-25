from fastapi import HTTPException, status


class PDFExtractionError(HTTPException):
    def __init__(self, detail: str = "Erro ao extrair texto do PDF"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class AnalysisProcessingError(HTTPException):
    def __init__(self, detail: str = "Erro ao processar a análise do currículo"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class AnalysisNotFoundError(HTTPException):
    def __init__(self, analysis_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Análise com ID {analysis_id} não encontrada",
        )
