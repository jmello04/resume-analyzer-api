"""Endpoint para análise de currículos em PDF."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.domain.schemas import AnalysisResponse
from app.infra.database.connection import get_db
from app.infra.database.repository import AnalysisRepository
from app.services.analyzer import analyze_resume
from app.services.pdf_extractor import extract_text_from_pdf

router = APIRouter()

_MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analisar currículo em PDF",
    description=(
        "Recebe um arquivo PDF via `multipart/form-data`, extrai o conteúdo textual "
        "e retorna uma avaliação estruturada com pontuação, nível profissional, "
        "pontos fortes, pontos fracos, sugestões de melhoria e habilidades detectadas."
    ),
)
async def analyze_resume_endpoint(
    file: UploadFile = File(..., description="Arquivo PDF do currículo (máx. 10 MB)"),
    db: Session = Depends(get_db),
) -> AnalysisResponse:
    """Recebe um currículo em PDF, executa a análise e persiste o resultado.

    Args:
        file: Arquivo PDF enviado via multipart/form-data.
        db: Sessão ativa do banco de dados (injetada via dependência).

    Returns:
        Registro de análise recém-criado com todos os campos avaliados.

    Raises:
        HTTPException 400: Arquivo sem extensão .pdf, vazio ou inválido.
        HTTPException 413: Arquivo excede o limite de 10 MB.
        HTTPException 422: Falha na extração de texto do PDF.
        HTTPException 500: Erro interno durante o processamento da análise.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas arquivos no formato PDF são aceitos.",
        )

    pdf_content = await file.read()

    if len(pdf_content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O arquivo enviado está vazio.",
        )

    if len(pdf_content) > _MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="O arquivo excede o tamanho máximo permitido de 10 MB.",
        )

    resume_text = extract_text_from_pdf(pdf_content)
    analysis_result = analyze_resume(resume_text)

    repo = AnalysisRepository(db)
    saved_record = repo.create(
        filename=file.filename,
        resume_text=resume_text,
        result=analysis_result,
    )

    return saved_record
