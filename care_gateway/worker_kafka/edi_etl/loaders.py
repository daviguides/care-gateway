import logging
import json
from pathlib import Path

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from care_gateway.db.sqlmodel_models.models import Claim, ClaimEvent
from care_gateway.worker_kafka.edi_etl.edi_transform import convert_to_claim_with_events

from care_gateway.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

DATA_DIR = "data"


async def save_claim_with_events(
    session: AsyncSession, claim: Claim, events: list[ClaimEvent]
) -> None:
    result = await session.exec(
        select(Claim).where(Claim.reference_id == claim.reference_id)
    )
    if result.first():
        logger.info(
            f"⚠️ Claim with reference_id '{claim.reference_id}' already exists. Skipping."
        )
        return

    session.add(claim)
    await session.flush()  # Populates claim.id so we can set it on events

    for event in events:
        event.claim_id = claim.id
        session.add(event)


async def load_claims_from_dicts(
    session: AsyncSession,
    claims_data: list[dict],
    outbox_path: Path,
) -> None:
    for claim_dict in claims_data:
        filename = f"{claim_dict.get('claim_id', 'claim_unknown')}.json"
        with open(DATA_DIR / outbox_path / filename, "w") as f:
            json.dump(claim_dict, f, indent=2)

        claim, events = convert_to_claim_with_events(claim_dict)
        await save_claim_with_events(session, claim, events)
