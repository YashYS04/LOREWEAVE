"""API v1 router — aggregates all endpoint routers."""

from fastapi import APIRouter

from app.ai.routers.ai import router as ai_router
from app.ai.routers.chat import chat_router
from app.api.v1.endpoints.characters import router as characters_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.locations import router as locations_router
from app.api.v1.endpoints.organizations import router as organizations_router
from app.api.v1.endpoints.relationships import router as relationships_router
from app.api.v1.endpoints.timeline import router as timeline_router
from app.api.v1.endpoints.universes import router as universes_router
from app.api.v1.endpoints.world_objects import router as world_objects_router
from app.api.v1.endpoints.world_rules import router as world_rules_router
from app.graph.router import router as graph_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(universes_router)
api_router.include_router(characters_router)
api_router.include_router(locations_router)
api_router.include_router(organizations_router)
api_router.include_router(world_objects_router)
api_router.include_router(world_rules_router)
api_router.include_router(relationships_router)
api_router.include_router(timeline_router)
api_router.include_router(graph_router)
api_router.include_router(ai_router)
api_router.include_router(chat_router)
