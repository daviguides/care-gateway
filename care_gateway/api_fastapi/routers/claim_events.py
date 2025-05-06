from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from care_gateway.db.sqlmodel_models.models import ClaimEvent
from care_gateway.db.sqlmodel_models.session import get_sqlmodel_session

router = APIRouter()


@router.get("/", response_model=List[ClaimEvent])
async def list_claim_events(session: AsyncSession = Depends(get_sqlmodel_session)):
    result = await session.exec(select(ClaimEvent))
    return result.all()


@router.get("/by-claim/{claim_id}", response_model=List[ClaimEvent])
async def list_events_by_claim(
    claim_id: int, session: AsyncSession = Depends(get_sqlmodel_session)
):
    """Return all events for a specific claim."""
    statement = select(ClaimEvent).where(ClaimEvent.claim_id == claim_id)
    result = await session.exec(statement)
    return result.all()


@router.get("/{event_id}", response_model=ClaimEvent)
async def get_event_by_id(
    event_id: str, session: AsyncSession = Depends(get_sqlmodel_session)
):
    event = await session.get(ClaimEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
