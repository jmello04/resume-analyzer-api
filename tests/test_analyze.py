from unittest.mock import patch

import pytest

from app.domain.models import AnalysisResult

MOCK_RESULT = AnalysisResult(
    score=80,
    level="Pleno",
    strong_points=["Strong Python skills", "Solid project portfolio"],
    weak_points=["No formal leadership experience"],
    suggestions=["Pursue cloud certifications", "Contribute to open source projects"],
    detected_skills=["Python", "FastAPI", "PostgreSQL", "Docker", "REST APIs"],
)

FAKE_PDF = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_missing_file(client):
    response = client.post("/analyze")
    assert response.status_code == 422


def test_analyze_wrong_file_type(client):
    response = client.post(
        "/analyze",
        files={"file": ("resume.txt", b"plain text content", "text/plain")},
    )
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


@patch("app.api.routes.analyze.analyzer")
@patch("app.api.routes.analyze.pdf_extractor")
def test_analyze_pdf_success(mock_extractor, mock_analyzer, client):
    mock_extractor.extract_text.return_value = "Jane Doe - Senior Software Engineer"
    mock_analyzer.analyze.return_value = MOCK_RESULT

    response = client.post(
        "/analyze",
        files={"file": ("resume.pdf", FAKE_PDF, "application/pdf")},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["score"] == 80
    assert data["level"] == "Pleno"
    assert isinstance(data["strong_points"], list)
    assert isinstance(data["weak_points"], list)
    assert isinstance(data["suggestions"], list)
    assert isinstance(data["detected_skills"], list)
    assert data["filename"] == "resume.pdf"
    assert "id" in data
    assert "created_at" in data


def test_get_history_returns_list(client):
    response = client.get("/history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_history_item_not_found(client):
    response = client.get("/history/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@patch("app.api.routes.analyze.analyzer")
@patch("app.api.routes.analyze.pdf_extractor")
def test_get_history_after_analysis(mock_extractor, mock_analyzer, client):
    mock_extractor.extract_text.return_value = "John Doe - Backend Developer"
    mock_analyzer.analyze.return_value = MOCK_RESULT

    client.post(
        "/analyze",
        files={"file": ("test_resume.pdf", FAKE_PDF, "application/pdf")},
    )

    response = client.get("/history")
    assert response.status_code == 200
    history = response.json()
    assert len(history) >= 1
    assert "score" in history[0]
    assert "level" in history[0]
    assert "filename" in history[0]
