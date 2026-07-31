"""Organization service."""

from app.models.organization import Organization
from app.repositories.organization import OrganizationRepository
from app.schemas.organization import OrganizationCreate
from app.services.base import EntityService


class OrganizationService(EntityService[Organization, OrganizationCreate, object]):
    repo_class = OrganizationRepository

    def _build(self, payload: OrganizationCreate, entity_id: str) -> Organization:
        return Organization(
            id=entity_id,
            universe_id=payload.universe_id,
            name=payload.name,
            type=payload.type,
            description=payload.description,
            leader=payload.leader,
            purpose=payload.purpose,
            notes=payload.notes,
        )
