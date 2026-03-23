# Resume Analyzer API

REST API for resume analysis with automatic scoring, skill detection, and structured feedback.

## Features

- PDF resume upload and text extraction
- Automated analysis with structured feedback
- Score from 0 to 100
- Career level classification (Júnior, Pleno, Sênior)
- Strong points, weak points, and improvement suggestions
- Skill detection
- Analysis history stored in PostgreSQL

## Requirements

- Docker and Docker Compose
- Anthropic API Key

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/jmello04/resume-analyzer-api.git
   cd resume-analyzer-api
   ```

2. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and set your `ANTHROPIC_API_KEY`.

## Running with Docker

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.

## API Documentation

Interactive Swagger documentation: `http://localhost:8000/docs`

ReDoc documentation: `http://localhost:8000/redoc`

## Endpoints

### POST /analyze

Upload a PDF resume for analysis.

**Request:** `multipart/form-data` with a `file` field containing the PDF.

**Response:**
```json
{
  "id": 1,
  "filename": "resume.pdf",
  "score": 78,
  "level": "Pleno",
  "strong_points": ["Strong Python skills", "Relevant project experience"],
  "weak_points": ["No leadership experience"],
  "suggestions": ["Add cloud certifications", "Contribute to open source"],
  "detected_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
  "created_at": "2024-01-01T00:00:00"
}
```

### GET /history

Returns a list of all previous analyses.

### GET /history/{id}

Returns a specific analysis by ID.

### GET /health

Health check endpoint.

## Running Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## Project Structure

```
resume-analyzer-api/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── analyze.py
│   │       └── history.py
│   ├── core/
│   │   └── config.py
│   ├── domain/
│   │   └── models.py
│   ├── infra/
│   │   └── database/
│   │       ├── connection.py
│   │       └── repositories.py
│   ├── services/
│   │   ├── pdf_extractor.py
│   │   └── analyzer.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   └── test_analyze.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```
