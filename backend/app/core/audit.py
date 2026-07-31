"""Structured audit logging for domain events."""

import logging
from datetime import UTC, datetime

logger = logging.getLogger("loreweave.audit")


def _now() -> str:
    return datetime.now(tz=UTC).isoformat()


def universe_created(universe_id: str, slug: str) -> None:
    logger.info(
        "UNIVERSE_CREATED id=%s slug=%s timestamp=%s",
        universe_id,
        slug,
        _now(),
    )


def universe_updated(universe_id: str, slug: str) -> None:
    logger.info(
        "UNIVERSE_UPDATED id=%s slug=%s timestamp=%s",
        universe_id,
        slug,
        _now(),
    )


def universe_deleted(universe_id: str, slug: str) -> None:
    logger.info(
        "UNIVERSE_DELETED id=%s slug=%s timestamp=%s",
        universe_id,
        slug,
        _now(),
    )


# ── Generic entity (used by Location, Organization, WorldObject, WorldRule) ────


def entity_created(table: str, entity_id: str, name: str) -> None:
    logger.info(
        "ENTITY_CREATED table=%s id=%s name=%s timestamp=%s",
        table,
        entity_id,
        name,
        _now(),
    )


def entity_updated(table: str, entity_id: str, name: str) -> None:
    logger.info(
        "ENTITY_UPDATED table=%s id=%s name=%s timestamp=%s",
        table,
        entity_id,
        name,
        _now(),
    )


def entity_deleted(table: str, entity_id: str, name: str) -> None:
    logger.info(
        "ENTITY_DELETED table=%s id=%s name=%s timestamp=%s",
        table,
        entity_id,
        name,
        _now(),
    )


# ── Character ──────────────────────────────────────────────────────────────────


def character_created(character_id: str, name: str, universe_id: str) -> None:
    logger.info(
        "CHARACTER_CREATED id=%s name=%s universe_id=%s timestamp=%s",
        character_id,
        name,
        universe_id,
        _now(),
    )


def character_updated(character_id: str, name: str) -> None:
    logger.info(
        "CHARACTER_UPDATED id=%s name=%s timestamp=%s",
        character_id,
        name,
        _now(),
    )


def character_deleted(character_id: str, name: str) -> None:
    logger.info(
        "CHARACTER_DELETED id=%s name=%s timestamp=%s",
        character_id,
        name,
        _now(),
    )


# ── Relationship ───────────────────────────────────────────────────────────────


def relationship_created(rel_id: str, rel_type: str, universe_id: str) -> None:
    logger.info(
        "RELATIONSHIP_CREATED id=%s type=%s universe_id=%s timestamp=%s",
        rel_id,
        rel_type,
        universe_id,
        _now(),
    )


def relationship_updated(rel_id: str, rel_type: str) -> None:
    logger.info(
        "RELATIONSHIP_UPDATED id=%s type=%s timestamp=%s",
        rel_id,
        rel_type,
        _now(),
    )


def relationship_deleted(rel_id: str, rel_type: str) -> None:
    logger.info(
        "RELATIONSHIP_DELETED id=%s type=%s timestamp=%s",
        rel_id,
        rel_type,
        _now(),
    )


# ── Timeline ───────────────────────────────────────────────────────────────────


def timeline_event_created(event_id: str, title: str, universe_id: str) -> None:
    logger.info(
        "TIMELINE_EVENT_CREATED id=%s title=%s universe_id=%s timestamp=%s",
        event_id,
        title,
        universe_id,
        _now(),
    )


def timeline_event_updated(event_id: str, title: str) -> None:
    logger.info(
        "TIMELINE_EVENT_UPDATED id=%s title=%s timestamp=%s",
        event_id,
        title,
        _now(),
    )


def timeline_event_deleted(event_id: str, title: str) -> None:
    logger.info(
        "TIMELINE_EVENT_DELETED id=%s title=%s timestamp=%s",
        event_id,
        title,
        _now(),
    )
