import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["SEED_ON_STARTUP"] = "false"

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.seed import seed

engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture()
def db() -> Iterator[Session]:
    Base.metadata.create_all(bind=engine)
    session = TestingSession()
    seed(session, quantidade_eventos=40)
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db: Session) -> Iterator[TestClient]:
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def autenticar(client: TestClient, email: str, senha: str) -> dict[str, str]:
    r = client.post("/api/auth/login", data={"username": email, "password": senha})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def admin(client: TestClient) -> dict[str, str]:
    return autenticar(client, "admin@starkbank.local", "admin123")


@pytest.fixture()
def leitor(client: TestClient) -> dict[str, str]:
    return autenticar(client, "auditor@starkbank.local", "auditor123")
