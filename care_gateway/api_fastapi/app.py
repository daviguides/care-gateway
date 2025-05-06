from contextlib import asynccontextmanager

from fastapi import FastAPI

from care_gateway.api_fastapi.routers import claim_events, claims
from care_gateway.db.sqlmodel_models.session import dispose_db, init_sqlmodel_db

tags_metadata = [
    {"name": "Claims", "description": "Healthcare claim submission and retrieval."},
    {"name": "Claim Events", "description": "Track the lifecycle of each claim."},
    {"name": "Health Check", "description": "Basic endpoint to verify system status."},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_sqlmodel_db()
    yield
    await dispose_db()


app = FastAPI(
    title="CareGateway API (FastAPI)",
    summary="Healthcare Claim Gateway API",
    description=(
        "An async REST API simulating healthcare claim workflows, part of the CareGateway project.\n\n"
        "It includes endpoints for managing claims and their associated events, built for high-performance "
        "use in data engineering and healthtech scenarios."
    ),
    version="1.0",
    contact={
        "name": "Davi Guides: Portfolio",
        "url": "https://daviguides.github.io/",
    },
    openapi_tags=tags_metadata,
    root_path="",
    debug=True,
    lifespan=lifespan,
)

# Mount routes
app.include_router(
    claims.router,
    prefix="/claims",
    tags=["Claims"],
)
app.include_router(
    claim_events.router,
    prefix="/claim_events",
    tags=["Claim Events"],
)
