from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.routers import alertas, auth, casos, classificacao, dashboard, eventos, ferramentas, tipos, usuarios
from app.seed import seed


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    if get_settings().seed_on_startup:
        with SessionLocal() as db:
            seed(db)
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (auth, usuarios, ferramentas, tipos, classificacao, eventos, alertas, casos, dashboard):
    app.include_router(router.router)


@app.get("/api/health", tags=["Infra"])
def health() -> dict[str, str]:
    return {"status": "ok"}
