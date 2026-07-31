"""GraphService — thin orchestration layer over GraphBuilder."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.graph.graph_builder import GraphBuilder
from app.graph.schemas import GraphResponse

logger = logging.getLogger(__name__)


class GraphService:
    """Thin service wrapper so the router stays clean and the builder is testable."""

    def __init__(self, session: AsyncSession) -> None:
        self._builder = GraphBuilder(session)

    async def get_graph(self, universe_id: str) -> GraphResponse | None:
        """Return the full graph for a universe or ``None`` if it doesn't exist."""
        return await self._builder.build(universe_id)
