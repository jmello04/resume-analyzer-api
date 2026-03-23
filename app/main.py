from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.infra.database.connection import create_tables
from app.api.routes import analyze, history


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="Resume Analyzer API",
    description="API for resume analysis with scoring, skill detection, and structured feedback.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(analyze.router, tags=["Analysis"])
app.include_router(history.router, tags=["History"])


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
