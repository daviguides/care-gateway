from fastapi import FastAPI
from care_gateway.api_fastapi.routers import claims, claim_events

app = FastAPI(title="CareGateway API (FastAPI)", version="1.0")

# Mount routes
app.include_router(claims.router, prefix="/claims", tags=["Claims"])
app.include_router(claim_events.router, prefix="/claim_events", tags=["Claim Events"])
