import logging
from pathlib import Path
from typing import Sequence

from care_gateway.db.sqlmodel_models.session import AsyncSessionLocal
from care_gateway.worker_kafka.edi_etl.loaders import load_claims_from_dicts
from care_gateway.worker_kafka.edi_etl.processor import parse_edi_files_individually

from care_gateway.utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


async def run_edi_etl() -> None:
    logger.info("🚀 Starting EDI ETL process...")

    inbox_path = Path("data/inbox")
    outbox_path = Path("data/out")
    outbox_path.mkdir(exist_ok=True)
    files = [p.name for p in inbox_path.glob("*.*")]

    raw_claims = parse_edi_files_individually(files)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            await load_claims_from_dicts(session, raw_claims, outbox_path)

    logger.info(f"✅ Processed and saved {len(raw_claims)} claims.")


async def run_edi_etl_for_s3_keys(s3_keys: Sequence[str]) -> None:
    logger.info(f"🚀 Starting EDI ETL for s3_keys: {s3_keys}")

    inbox_path = Path("data/inbox")
    outbox_path = Path("data/out")
    outbox_path.mkdir(exist_ok=True)

    # Resolve paths based on s3_keys
    local_files = []
    for key in s3_keys:
        path = inbox_path / key
        if path.exists():
            local_files.append(key)
        else:
            logger.info(f"⚠️ Skipping missing file: {path}")

    if not local_files:
        logger.info("❌ No valid files found to process.")
        return

    raw_claims = parse_edi_files_individually(
        local_files,
        inbox_dir=inbox_path,
    )

    async with AsyncSessionLocal() as session:
        async with session.begin():
            await load_claims_from_dicts(session, raw_claims, outbox_path)

    logger.info(f"✅ Processed and saved {len(raw_claims)} claims.")
