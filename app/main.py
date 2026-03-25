import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import analyze, history
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.infra.database.connection import engine
from app.infra.database.models import Base

setup_logging(debug=settings.DEBUG)
logger = get_logger("resume_analyzer.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicação — criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    logger.info("Aplicação pronta para receber requisições.")
    yield
    logger.info("Encerrando aplicação.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "API REST para análise automatizada de currículos em PDF. "
        "Extrai o conteúdo textual dos documentos e retorna uma avaliação estruturada "
        "com pontuação (0–100), nível profissional, pontos fortes, pontos fracos, "
        "sugestões de melhoria e habilidades técnicas identificadas."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start = time.perf_counter()

    logger.info(
        "Requisição recebida | id=%s | %s %s",
        request_id,
        request.method,
        request.url.path,
    )

    response = await call_next(request)
    elapsed = (time.perf_counter() - start) * 1000

    logger.info(
        "Requisição concluída | id=%s | status=%d | %.1fms",
        request_id,
        response.status_code,
        elapsed,
    )

    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Erro não tratado em %s %s: %s",
        request.method,
        request.url.path,
        str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor. Tente novamente mais tarde."},
    )


app.include_router(
    analyze.router,
    prefix="/api/v1",
    tags=["Análise de Currículo"],
)

app.include_router(
    history.router,
    prefix="/api/v1",
    tags=["Histórico"],
)


@app.get("/", tags=["Status"], summary="Informações da API")
def root() -> dict:
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health", tags=["Status"], summary="Verificação de saúde")
def health_check() -> dict:
    return {"status": "healthy"}
