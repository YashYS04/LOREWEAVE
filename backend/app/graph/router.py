"""Graph API router.

GET /api/v1/graph/{universe_id}
    Returns the full knowledge graph (nodes, edges, statistics) for a universe.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.graph.graph_service import GraphService
from app.schemas.response import success

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/graph", tags=["graph"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


def _get_service(db: DbDep) -> GraphService:
    return GraphService(db)


ServiceDep = Annotated[GraphService, Depends(_get_service)]


@router.get(
    "/{universe_id}",
    summary="Get the knowledge graph for a universe",
    description=(
        "Returns all nodes (entities) and edges (relationships) for the universe, "
        "plus graph statistics: node/edge counts, connected components, average degree."
    ),
)
async def get_graph(universe_id: str, svc: ServiceDep) -> JSONResponse:
    graph = await svc.get_graph(universe_id)
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Universe not found",
        )
    return JSONResponse(
        content=success(
            data=graph.model_dump(mode="json"),
            message="OK",
        )
    )
