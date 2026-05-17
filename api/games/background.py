"""
Background task runner for game analysis.
Uses its own SQLAlchemy session since the request session closes
immediately when the 202 response is sent.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.config import get_settings
from worker.pipeline.orchestrator import analyze_game


def run_analysis_background(game_id: str, db_url: str | None = None) -> None:
    """
    Runs in a FastAPI background thread.
    Creates its own DB session independent of the request lifecycle.
    """
    settings = get_settings()
    url = db_url or str(settings.database_url)
    
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        
    engine = create_engine(
        url,
        connect_args=connect_args,
    )
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        analyze_game(db, game_id)
    finally:
        db.close()
        engine.dispose()
