from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.domain.models import AnalysisResponse
from app.infra.database.connection import get_db
from app.infra.database.repositories import AnalysisRepository
from app.services.analyzer import ResumeAnalyzerService
from app.services.pdf_extractor import PDFExtractorService

router = APIRouter()

pdf_extractor = PDFExtractorService()
analyzer = ResumeAnalyzerService()


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    status_code=201,
    summary="Analyze a resume",
    description="Upload a PDF resume and receive a structured evaluation with score, level, strengths, weaknesses, suggestions, and detected skills.",
)
async def analyze_resume(
    file: UploadFile = File(..., description="Resume file in PDF format"),
    db: Session = Depends(get_db),
) -> AnalysisResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    file_bytes = await file.read()

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    try:
        text = pdf_extractor.extract_text(file_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=422, detail="Failed to process the PDF file.")

    try:
        result = analyzer.analyze(text)
    except Exception:
        raise HTTPException(status_code=502, detail="Analysis service is currently unavailable.")

    repo = AnalysisRepository(db)
    record = repo.save(file.filename, text, result)
    return record
