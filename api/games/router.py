from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from api.database import get_db
from api.games.models import GameReportResponse, GameResponse, MoveEvaluationResponse
from api.games.service import (
    InvalidPGNError,
    create_game_from_upload,
    get_game,
    list_games,
    list_move_evaluations,
)
from worker.pipeline.orchestrator import AnalysisError, analyze_game
from api.games.background import run_analysis_background
from api.config import get_settings
from api.models import User
from api.auth.dependencies import get_current_user

router = APIRouter(prefix="/games", tags=["games"])


@router.post("", response_model=GameResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_game(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GameResponse:
    try:
        return await create_game_from_upload(db, file, current_user.id)
    except InvalidPGNError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("", response_model=list[GameResponse])
def read_games(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[GameResponse]:
    return list_games(db, current_user.id)


@router.get("/{game_id}", response_model=GameResponse)
def read_game(
    game_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GameResponse:
    game = get_game(db, game_id, current_user.id)
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found.",
        )
    return game


@router.post(
    "/{game_id}/analyze",
    response_model=GameResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def run_local_analysis(
    game_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GameResponse:
    game = get_game(db, game_id, current_user.id)
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found.",
        )
    if game.status == "processing":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Analysis already in progress.",
        )
    # Mark as processing immediately so the frontend can show progress
    game.status = "processing"
    game.error_message = None
    db.commit()
    db.refresh(game)

    # Queue the heavy pipeline (Stockfish + RAG + Gemini) in the background
    settings = get_settings()
    background_tasks.add_task(run_analysis_background, game_id, str(settings.database_url))
    return game


@router.get("/{game_id}/report", response_model=GameReportResponse)
def read_game_report(
    game_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    game = get_game(db, game_id, current_user.id)
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found.",
        )
    if game.status != "complete" or game.report is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Report is not ready yet.",
        )
    return game.report


@router.get("/{game_id}/moves", response_model=list[MoveEvaluationResponse])
def read_move_evaluations(
    game_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MoveEvaluationResponse]:
    if get_game(db, game_id, current_user.id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found.",
        )
    return list_move_evaluations(db, game_id)
