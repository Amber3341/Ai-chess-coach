import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import get_settings
from api.database import init_db
from api.games.router import router as games_router
from api.auth.router import router as auth_router
from api.users.router import router as users_router


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


settings = get_settings()

app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(users_router, prefix=settings.api_prefix)
app.include_router(games_router, prefix=settings.api_prefix)


# Route alias to support standard Pub/Sub endpoint format from guides
from api.games.router import handle_pubsub_analyze_push, PubSubPushRequest
from api.database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session

@app.post("/api/v1/internal/pubsub/analyze", status_code=200, tags=["games"])
def handle_pubsub_analyze_push_alias(
    request: PubSubPushRequest,
    db: Session = Depends(get_db),
):
    return handle_pubsub_analyze_push(request, db)
