"""Universe service — business logic layer."""

import logging
import re
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import audit
from app.models.universe import Universe, UniverseStatus
from app.repositories.universe import UniverseRepository
from app.schemas.universe import UniverseCreate, UniverseUpdate

logger = logging.getLogger(__name__)


def _slugify(text: str) -> str:
    """Convert a name into a URL-safe lowercase slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


class UniverseService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = UniverseRepository(session)

    async def _unique_slug(self, base: str) -> str:
        """Ensure the slug is unique by appending a short UUID suffix if needed."""
        slug = _slugify(base)
        if not await self._repo.slug_exists(slug):
            return slug
        suffix = uuid.uuid4().hex[:6]
        return f"{slug}-{suffix}"

    async def create_universe(self, payload: UniverseCreate) -> Universe:
        slug = await self._unique_slug(payload.name)
        universe = Universe(
            id=str(uuid.uuid4()),
            name=payload.name,
            slug=slug,
            genre=payload.genre.value,
            description=payload.description,
            tone=payload.tone,
            target_audience=payload.target_audience,
            status=UniverseStatus.draft.value,
        )
        result = await self._repo.create(universe)
        audit.universe_created(result.id, result.slug)
        return result

    async def get_by_id(self, universe_id: str) -> Universe | None:
        return await self._repo.get_by_id(universe_id)

    async def get_by_slug(self, slug: str) -> Universe | None:
        return await self._repo.get_by_slug(slug)

    async def list_universes(
        self, skip: int = 0, limit: int = 50
    ) -> tuple[list[Universe], int]:
        universes = await self._repo.list_all(skip=skip, limit=limit)
        total = await self._repo.count()
        return universes, total

    async def update_universe(
        self, universe_id: str, payload: UniverseUpdate
    ) -> Universe | None:
        universe = await self._repo.get_by_id(universe_id)
        if not universe:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field in ("genre", "status") and value is not None:
                value = value.value if hasattr(value, "value") else value
            setattr(universe, field, value)

        result = await self._repo.update(universe)
        audit.universe_updated(result.id, result.slug)
        return result

    async def delete_universe(self, universe_id: str) -> bool:
        universe = await self._repo.get_by_id(universe_id)
        if not universe:
            return False
        await self._repo.soft_delete(universe)
        audit.universe_deleted(universe.id, universe.slug)
        return True
