"""
session_helper (aliased as sh) contains a number of convenience
functions for workings with a SQLAlchemy session
"""
from typing import Any, Optional, Sequence

import sqlalchemy as sa
from sqlalchemy import update, ColumnElement, Row
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.helpers.session.parser import BulkActionParser
from src.db.models.templates import Base, StandardBase
from src.db.templates.markers.bulk.delete import BulkDeletableModel
from src.db.templates.markers.bulk.insert import BulkInsertableModel
from src.db.templates.markers.bulk.update import BulkUpdatableModel
from src.db.templates.markers.bulk.upsert import BulkUpsertableModel
from src.db.templates.protocols.has_id import HasIDProtocol


async def one_or_none(
    session: AsyncSession,
    query: sa.Select
) -> sa.Row | None:
    raw_result = await session.execute(query)
    return raw_result.scalars().one_or_none()

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

async def mappings(session: AsyncSession, query: sa.Select) -> Sequence[sa.RowMapping]:
    raw_result = await session.execute(query)
    return raw_result.mappings().all()

async def bulk_upsert(
    session: AsyncSession,
    models: list[BulkUpsertableModel],
):
    if len(models) == 0:
        return
    parser = BulkActionParser(models)

    query = pg_insert(parser.sa_model)

    upsert_mappings = [upsert_model.model_dump() for upsert_model in models]

    set_ = {}
    for k, v in upsert_mappings[0].items():
        if k == parser.id_field:
            continue
        set_[k] = getattr(query.excluded, k)

    query = query.on_conflict_do_update(
        index_elements=[parser.id_field],
        set_=set_
    )

    # Note, mapping must include primary key
    await session.execute(
        statement=query,
        params=upsert_mappings
    )

async def add(
    session: AsyncSession,
    model: Base,
    return_id: bool = False
) -> int | None:
    session.add(model)
    if return_id:
        if not isinstance(model, HasIDProtocol):
            raise AttributeError("Models must have an id attribute")
        await session.flush()
        return model.id
    return None


async def add_all(
    session: AsyncSession,
    models: list[StandardBase],
    return_ids: bool = False
) -> list[int] | None:
    session.add_all(models)
    if return_ids:
        if not isinstance(models[0], HasIDProtocol):
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
) -> Sequence[Row]:
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


async def bulk_delete(session: AsyncSession, models: list[BulkDeletableModel]):
    """Bulk delete sqlalchemy models of the same type."""
    if len(models) == 0:
        return

    parser = BulkActionParser(models)

    # Use declared field names from the model (excludes properties/methods)
    field_names = parser.get_all_fields()

    sa_model = parser.sa_model

    # Get value tuples to be used in identifying attributes for bulk delete
    value_tuples = []
    for model in models:
        tup = tuple(getattr(model, field) for field in field_names)
        value_tuples.append(tup)


    statement = (
        sa.delete(
            sa_model
        ).where(
            sa.tuple_(
                *[
                    getattr(sa_model, attr)
                    for attr in field_names
                ]
            ).in_(value_tuples)
        )
    )

    await session.execute(statement)

async def bulk_insert(
    session: AsyncSession,
    models: list[BulkInsertableModel],
    return_ids: bool = False
) -> list[int] | None:
    """Bulk insert sqlalchemy models via their pydantic counterparts."""

    if len(models) == 0:
        return None

    parser = BulkActionParser(models)
    sa_model = parser.sa_model

    models_to_add = []
    for model in models:
        sa_model_instance = sa_model(**model.model_dump())
        models_to_add.append(sa_model_instance)

    return await add_all(
        session=session,
        models=models_to_add,
        return_ids=return_ids
    )

async def bulk_update(
    session: AsyncSession,
    models: list[BulkUpdatableModel],
):
    """Bulk update sqlalchemy models via their pydantic counterparts."""
    if len(models) == 0:
        return

    parser = BulkActionParser(models)

    sa_model = parser.sa_model
    id_field = parser.id_field
    update_fields = parser.get_non_id_fields()


    for model in models:
        update_values = {
            k: getattr(model, k)
            for k in update_fields
        }
        id_value = getattr(model, id_field)
        id_attr: ColumnElement = getattr(sa_model, id_field)
        stmt = (
            update(sa_model)
            .where(
                id_attr == id_value
            )
            .values(**update_values)
        )
        await session.execute(stmt)


