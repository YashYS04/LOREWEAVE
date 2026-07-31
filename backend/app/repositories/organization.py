"""Organization repository."""

from app.models.organization import Organization
from app.repositories.base import EntityRepository


class OrganizationRepository(EntityRepository[Organization]):
    model = Organization
