from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import Session, select
from care_gateway.db.database import get_sqlmodel_session
from care_gateway.db.sqlmodel_models.models import Claim

router = APIRouter()


@router.get("/", response_model=List[Claim])
def list_claims(session: Session = Depends(get_sqlmodel_session)):
    return session.exec(select(Claim)).all()


@router.get("/{claim_id}", response_model=Claim)
def get_claim_by_id(claim_id: str, session: Session = Depends(get_sqlmodel_session)):
    claim = session.get(Claim, claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim
