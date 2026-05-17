import logging
from pathlib import Path

from google.cloud import storage

from api.config import get_settings

logger = logging.getLogger(__name__)

def get_storage_client():
    """Returns a GCS client if configured, else None."""
    settings = get_settings()
    if settings.gcp_project_id and settings.gcs_bucket_name:
        try:
            return storage.Client(project=settings.gcp_project_id)
        except Exception as e:
            logger.warning(f"Failed to initialize GCS client: {e}")
    return None

def save_pgn(game_id: str, content: str) -> str:
    """
    Saves the PGN content to GCS if configured, otherwise falls back to local disk.
    Returns the URI of the saved file (e.g., 'gs://bucket/file.pgn' or 'file://path/to/file.pgn').
    """
    settings = get_settings()
    client = get_storage_client()
    
    if client and settings.gcs_bucket_name:
        try:
            bucket = client.bucket(settings.gcs_bucket_name)
            blob = bucket.blob(f"{game_id}.pgn")
            blob.upload_from_string(content, content_type="application/x-chess-pgn")
            uri = f"gs://{settings.gcs_bucket_name}/{game_id}.pgn"
            logger.info(f"Saved PGN to GCS: {uri}")
            return uri
        except Exception as e:
            logger.error(f"Error saving to GCS, falling back to local: {e}")
            
    # Local fallback
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = settings.upload_dir / f"{game_id}.pgn"
    file_path.write_text(content, encoding="utf-8")
    uri = f"file://{file_path.absolute()}"
    logger.info(f"Saved PGN locally: {uri}")
    return uri

def get_pgn(game_id: str) -> str:
    """
    Retrieves the PGN content from GCS if configured, otherwise falls back to local disk.
    """
    settings = get_settings()
    client = get_storage_client()
    
    if client and settings.gcs_bucket_name:
        try:
            bucket = client.bucket(settings.gcs_bucket_name)
            blob = bucket.blob(f"{game_id}.pgn")
            if blob.exists():
                content = blob.download_as_text()
                logger.info(f"Downloaded PGN from GCS: gs://{settings.gcs_bucket_name}/{game_id}.pgn")
                return content
        except Exception as e:
            logger.error(f"Error reading from GCS, attempting local fallback: {e}")
            
    # Local fallback
    file_path = settings.upload_dir / f"{game_id}.pgn"
    if file_path.exists():
        content = file_path.read_text(encoding="utf-8")
        logger.info(f"Read PGN locally: {file_path}")
        return content
        
    raise FileNotFoundError(f"PGN file for game {game_id} not found in GCS or locally.")
