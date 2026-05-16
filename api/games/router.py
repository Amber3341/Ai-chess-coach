from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from api.database import get_db
from api.games.models import GameReportResponse, GameResponse, MoveEvaluationResponse
from api.games.service import (
    InvalidPGNError,
    create_game_from_upload,
    get_game,
    list_move_evaluations,
)
from worker.pipeline.orchestrator import AnalysisError, analyze_game

router = APIRouter(prefix="/games", tags=["games"])


@router.post("", response_model=GameResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_game(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> GameResponse:
    try:
        return await create_game_from_upload(db, file)
    except InvalidPGNError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get("/{game_id}", response_model=GameResponse)
def read_game(game_id: str, db: Session = Depends(get_db)) -> GameResponse:
    game = get_game(db, game_id)
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found.",
        )
    return game


@router.post("/{game_id}/analyze", response_model=GameResponse)
def run_local_analysis(game_id: str, db: Session = Depends(get_db)) -> GameResponse:
    try:
        return analyze_game(db, game_id)
    except AnalysisError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get("/{game_id}/report", response_model=GameReportResponse)
def read_game_report(game_id: str, db: Session = Depends(get_db)) -> dict:
    game = get_game(db, game_id)
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
    game_id: str, db: Session = Depends(get_db)
) -> list[MoveEvaluationResponse]:
    if get_game(db, game_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found.",
        )
    return list_move_evaluations(db, game_id)
