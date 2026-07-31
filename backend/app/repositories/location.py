"""Location repository."""

from app.models.location import Location
from app.repositories.base import EntityRepository


class LocationRepository(EntityRepository[Location]):
    model = Location
