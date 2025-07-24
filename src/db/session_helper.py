"""
session_helper (aliased as sh) contains a number of convenience
functions for workings with a SQLAlchemy session
"""
from typing import Any, Optional

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.db.models.templates import Base
from src.db.templates.upsert import UpsertModel


async def scalar(session: AsyncSession, query: sa.Select) -> Any:
    """Fetch the first column of the first row."""
    raw_result = await session.execute(query)
    return raw_result.scalar()

async def scalars(session: AsyncSession, query: sa.Select) -> Any:
    raw_result = await session.execute(query)
    return raw_result.scalars().all()

async def mapping(session: AsyncSession, query: sa.Select) -> sa.RowMapping:
    raw_result = await session.execute(query)
    return raw_result.mappings().one()


async def bulk_upsert(
    session: AsyncSession,
    models: list[UpsertModel],
):
    if len(models) == 0:
        return

    first_model = models[0]

    query = pg_insert(first_model.sa_model)

    mappings = [upsert_model.model_dump() for upsert_model in models]

    set_ = {}
    for k, v in mappings[0].items():
        if k == first_model.id_field:
            continue
        set_[k] = getattr(query.excluded, k)

    query = query.on_conflict_do_update(
        index_elements=[first_model.id_field],
        set_=set_
    )

    # Note, mapping must include primary key
    await session.execute(
        query,
        mappings
    )

async def add(
    session: AsyncSession,
    model: Base,
    return_id: bool = False
) -> int | None:
    session.add(model)
    if return_id:
        if not hasattr(model, "id"):
            raise AttributeError("Models must have an id attribute")
        await session.flush()
        return model.id
    return None


async def add_all(
    session: AsyncSession,
    models: list[Base],
    return_ids: bool = False
) -> list[int] | None:
    session.add_all(models)
    if return_ids:
        if not hasattr(models[0], "id"):
            raise AttributeError("Models must have an id attribute")
        await session.flush()
        return [
            model.id  # pyright: ignore [reportAttributeAccessIssue]
            for model in models
        ]
    return None

async def get_all(
    session: AsyncSession,
    model: Base,
    order_by_attribute: Optional[str] = None
) -> list[Base]:
    """
    Get all records of a model
    Used primarily in testing
    """
    statement = sa.select(model)
    if order_by_attribute:
        statement = statement.order_by(getattr(model, order_by_attribute))
    result = await session.execute(statement)
    return result.scalars().all()

def compile_to_sql(statement) -> str:
    compiled_sql = statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
    return compiled_sql