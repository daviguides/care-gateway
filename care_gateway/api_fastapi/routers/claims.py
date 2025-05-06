from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from care_gateway.db.sqlmodel_models.models import Claim
from care_gateway.db.sqlmodel_models.session import get_sqlmodel_session

router = APIRouter()


@router.get("/", response_model=List[Claim])
async def list_claims(session: AsyncSession = Depends(get_sqlmodel_session)):
    result = await session.exec(select(Claim))
    return result.all()


@router.get("/{claim_id}", response_model=Claim)
async def get_claim_by_id(
    claim_id: str, session: AsyncSession = Depends(get_sqlmodel_session)
):
    claim = await session.get(Claim, claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim
