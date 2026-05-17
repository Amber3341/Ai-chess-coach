import json
import logging
from typing import Optional

from google.cloud import pubsub_v1

from api.config import get_settings

logger = logging.getLogger(__name__)

# Global publisher client to reuse the connection pool
_publisher: Optional[pubsub_v1.PublisherClient] = None

def get_publisher() -> Optional[pubsub_v1.PublisherClient]:
    global _publisher
    settings = get_settings()
    if settings.gcp_project_id and settings.gcp_pubsub_topic_id:
        if _publisher is None:
            try:
                _publisher = pubsub_v1.PublisherClient()
            except Exception as e:
                logger.warning(f"Failed to initialize Pub/Sub client: {e}")
        return _publisher
    return None

def publish_analyze_job(game_id: str) -> bool:
    """
    Publishes an analysis job to Pub/Sub.
    Returns True if published, False if Pub/Sub is not configured (triggering local fallback).
    """
    settings = get_settings()
    publisher = get_publisher()
    
    if publisher and settings.gcp_project_id and settings.gcp_pubsub_topic_id:
        topic_path = publisher.topic_path(settings.gcp_project_id, settings.gcp_pubsub_topic_id)
        message_json = json.dumps({"game_id": game_id})
        message_bytes = message_json.encode("utf-8")
        
        try:
            future = publisher.publish(topic_path, data=message_bytes)
            message_id = future.result()
            logger.info(f"Published analysis job for game {game_id} to Pub/Sub (msg id: {message_id})")
            return True
        except Exception as e:
            logger.error(f"Failed to publish to Pub/Sub: {e}")
            return False
            
    return False
