import json
import logging
from pathlib import Path

from care_gateway.db.sqlmodel_models.session import AsyncSessionLocal
from care_gateway.worker_kafka.edi_etl.loaders import load_claims_from_dicts
from care_gateway.worker_kafka.edi_etl.processor import parse_edi_files_individually
from care_gateway.utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


async def handle_kafka_event(event_data: str) -> None:
    logger.info(f"📥 Received file event: {event_data}")
    event_dict = json.loads(event_data)
    s3_key = event_dict["s3_key"]

    file_path = Path("data/inbox") / s3_key
    if not file_path.exists():
        logger.info(f"⚠️ File not found: {file_path}")
        return

    raw_claims = parse_edi_files_individually([s3_key])

    async with AsyncSessionLocal() as session:
        async with session.begin():
            await load_claims_from_dicts(session, raw_claims, Path("out"))
