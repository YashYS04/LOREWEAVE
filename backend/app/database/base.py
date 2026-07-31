"""SQLAlchemy declarative base shared across all models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Project-wide SQLAlchemy base class.

    All ORM models must inherit from this class so that Alembic and the
    startup migration hook can discover them automatically.
    """
