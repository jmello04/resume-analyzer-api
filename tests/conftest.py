import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Variáveis de ambiente devem ser definidas ANTES de importar qualquer módulo da aplicação
os.environ.setdefault("ANALYSIS_API_KEY", "placeholder-for-tests")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_resume_analyzer.db")

from app.infra.database.connection import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

_SQLITE_TEST_URL = "sqlite:///./test_resume_analyzer.db"

_test_engine = create_engine(
    _SQLITE_TEST_URL,
    connect_args={"check_same_thread": False},
)
_TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)


def _override_get_db():
    db = _TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def client():
    Base.metadata.create_all(bind=_test_engine)
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=_test_engine)
    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
def _cleanup_test_db():
    yield
    _test_engine.dispose()
    db_path = "./test_resume_analyzer.db"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass
