from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import Session, select
from care_gateway.db.database import get_sqlmodel_session
from care_gateway.db.sqlmodel_models.models import ClaimEvent

router = APIRouter()


@router.get("/", response_model=List[ClaimEvent])
def list_claim_events(session: Session = Depends(get_sqlmodel_session)):
    return session.exec(select(ClaimEvent)).all()


@router.get("/by-claim/{claim_id}", response_model=List[ClaimEvent])
def list_events_by_claim(
    claim_id: int, session: Session = Depends(get_sqlmodel_session)
):
    """Return all events for a specific claim."""
    statement = select(ClaimEvent).where(ClaimEvent.claim_id == claim_id)
    return session.exec(statement).all()


@router.get("/{event_id}", response_model=ClaimEvent)
def get_event_by_id(event_id: str, session: Session = Depends(get_sqlmodel_session)):
    event = session.get(ClaimEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
