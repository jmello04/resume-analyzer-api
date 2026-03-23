import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

os.environ.setdefault("ANTHROPIC_API_KEY", "test_key_placeholder")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_resume.db")

TEST_DB_URL = "sqlite:///./test_resume.db"


@pytest.fixture(scope="session")
def db_engine():
    from app.infra.database.connection import Base

    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_resume.db"):
        os.remove("test_resume.db")


@pytest.fixture(scope="session")
def client(db_engine):
    from app.infra.database.connection import get_db
    from app.main import app

    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with patch("app.main.create_tables", return_value=None):
        with TestClient(app) as test_client:
            yield test_client

    app.dependency_overrides.clear()
