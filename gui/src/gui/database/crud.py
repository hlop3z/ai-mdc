from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, Sequence

from sqlalchemy import create_engine, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from ..utils.time import Date
from .base import BaseModel

T = TypeVar("T")  # SQLAlchemy model type


class BaseCRUD(Generic[T]):
    def __init__(self, model: Type[T], max_per_page: int = 100):
        self.model = model
        self.max_per_page = max_per_page

    def paginate(self, page: int = 1, items_per_page: int = 10) -> tuple[int, int]:
        page = max(1, page)
        limit = min(items_per_page, self.max_per_page)
        offset = (page - 1) * limit
        return offset, limit

    def statement_filter(
        self,
        page: int = 1,
        items_per_page: int = 10,
        conditions: Optional[Sequence[Any]] = None,
    ):
        offset, limit = self.paginate(page, items_per_page)
        stmt = select(self.model)
        if conditions:
            stmt = stmt.filter(*conditions)
        return stmt.offset(offset).limit(limit)

    def statement_filter_by(
        self,
        filters: Dict[str, Any],
        page: int = 1,
        items_per_page: int = 10,
    ):
        offset, limit = self.paginate(page, items_per_page)
        return select(self.model).filter_by(**filters).offset(offset).limit(limit)

    def statement_get(self, id: Any):
        return select(self.model).where(self.model.id == id)

    def create_instance(self, obj_in: Dict[str, Any]) -> T:
        return self.model(**obj_in)

    def update_instance(self, db_obj: T, obj_in: Dict[str, Any]) -> T:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        return db_obj


class CRUDAsync(BaseCRUD[T]):
    async def filter(
        self,
        db: AsyncSession,
        page: int = 1,
        items_per_page: int = 10,
        conditions: Optional[Sequence[Any]] = None,
    ) -> List[T]:
        result = await db.execute(
            self.statement_filter(page, items_per_page, conditions)
        )
        return result.scalars().all()

    async def filter_by(self, db: AsyncSession, filters: Dict[str, Any]) -> List[T]:
        stmt = self.statement_filter_by(filters)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def detail(self, db: AsyncSession, id: Any) -> Optional[T]:
        result = await db.execute(self.statement_get(id))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, obj_in: Dict[str, Any]) -> T:
        db_obj = self.create_instance(obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, id: Any, obj_in: Dict[str, Any]
    ) -> Optional[T]:
        db_obj = await self.detail(db, id)
        if not db_obj:
            return None
        self.update_instance(db_obj, obj_in)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: Any) -> bool:
        obj = await self.detail(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
            return True
        return False

    async def soft_delete(self, db: AsyncSession, id: Any) -> bool:
        obj = await self.detail(db, id)
        if obj:
            obj.deleted_at = Date.datetime()
            await db.commit()
            return True
        return False


class CRUDSync(BaseCRUD[T]):
    def filter(
        self,
        db: Session,
        page: int = 1,
        items_per_page: int = 10,
        conditions: Optional[Sequence[Any]] = None,
    ) -> List[T]:
        return db.scalars(self.statement_filter(page, items_per_page, conditions)).all()

    def filter_by(self, db: Session, filters: Dict[str, Any]) -> List[T]:
        return db.scalars(self.statement_filter_by(filters)).all()

    def detail(self, db: Session, id: Any) -> Optional[T]:
        return db.scalar(self.statement_get(id))

    def create(self, db: Session, obj_in: Dict[str, Any]) -> T:
        db_obj = self.create_instance(obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, id: Any, obj_in: Dict[str, Any]) -> Optional[T]:
        db_obj = self.detail(db, id)
        if not db_obj:
            return None
        self.update_instance(db_obj, obj_in)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: Any) -> bool:
        obj = self.detail(db, id)
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False

    def soft_delete(self, db: Session, id: Any) -> bool:
        obj = self.detail(db, id)
        if obj:
            obj.deleted_at = Date.datetime()
            db.commit()
            return True
        return False


class CRUD:
    """
    Factory for creating sync or async CRUD clients.
    """

    base = BaseModel

    def __init__(self, sync: bool = True, max_per_page: int = 100):
        self.sync = sync
        self.max_per_page = max_per_page
        self._engine = None

    def crud(self, model: Type[T]) -> Union[CRUDSync[T], CRUDAsync[T]]:
        if self.sync:
            return CRUDSync(model, self.max_per_page)
        return CRUDAsync(model, self.max_per_page)

    def engine(self, url: str, echo: bool = False):
        engine = (
            create_engine(url, echo=echo)
            if self.sync
            else create_async_engine(url, echo=echo, future=True)
        )
        self._engine = engine
        return engine

    def session(self, engine: Any):
        if self.sync:
            return sessionmaker(bind=engine, autocommit=False, autoflush=False)
        return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    def create_all(self):
        if self._engine:
            self.base.metadata.create_all(bind=self._engine)
        else:
            raise ValueError("SQLAlchemy Engine Not Found.")
