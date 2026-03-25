from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.domain.schemas import AnalysisResponse
from app.infra.database.connection import get_db
from app.infra.database.repository import AnalysisRepository
from app.services.analyzer import analyze_resume
from app.services.pdf_extractor import extract_text_from_pdf

router = APIRouter()

_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


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
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas arquivos no formato PDF são aceitos.",
        )

    content = await file.read()

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O arquivo enviado está vazio.",
        )

    if len(content) > _MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="O arquivo excede o tamanho máximo permitido de 10 MB.",
        )

    resume_text = extract_text_from_pdf(content)
    result = analyze_resume(resume_text)

    repo = AnalysisRepository(db)
    record = repo.create(
        filename=file.filename,
        resume_text=resume_text,
        result=result,
    )

    return record
