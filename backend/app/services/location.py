"""Location service."""

from app.models.location import Location
from app.repositories.location import LocationRepository
from app.schemas.location import LocationCreate
from app.services.base import EntityService


class LocationService(EntityService[Location, LocationCreate, object]):
    repo_class = LocationRepository

    def _build(self, payload: LocationCreate, entity_id: str) -> Location:
        return Location(
            id=entity_id,
            universe_id=payload.universe_id,
            name=payload.name,
            type=payload.type,
            description=payload.description,
            climate=payload.climate,
            culture=payload.culture,
            population=payload.population,
            notes=payload.notes,
        )
