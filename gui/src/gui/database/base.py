from typing import Any, Optional, Union

from sqlalchemy import Column, DateTime, Integer, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

from ..utils.time import Date

Base = declarative_base()


class Controller:
    """Database controller for both sync and async operations."""

    def _create_engine(self, echo: bool) -> Union[AsyncEngine, Any]:
        return (
            create_engine(self.url, echo=echo)
            if self.sync
            else create_async_engine(self.url, echo=echo, future=True)
        )

    def _create_session(self) -> Union[scoped_session, sessionmaker]:
        if self.sync:
            factory = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            return scoped_session(factory)
        return sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    def __init__(
        self, url: str = "sqlite:///db.sqlite3", echo: bool = False, sync: bool = True
    ):
        self.url = url
        self.sync = sync
        self.engine = self._create_engine(echo)
        self.session = self._create_session()

    def create_all(self):
        """Create all tables from Base metadata (only works in sync mode)."""
        if self.sync:
            Base.metadata.create_all(self.engine)
        else:
            raise RuntimeError(
                "Use `run_sync(Base.metadata.create_all)` inside async context for async engines."
            )


class BaseModel(Base):
    """Abstract base model for all tables."""

    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=Date.datetime())
    updated_at = Column(DateTime, default=Date.datetime(), onupdate=Date.datetime())
    deleted_at = Column(DateTime, nullable=True)

    def to_dict(self, exclude: Optional[list[str]] = None) -> dict:
        exclude = set(exclude or [])
        return {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs
            if c.key not in exclude
        }
