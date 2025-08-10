from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync.data_sources.params import DataSourcesSyncParameters
from src.db.models.instantiations.state.sync.data_sources import DataSourcesSyncState
from src.db.queries.base.builder import QueryBuilderBase


class GetDataSourcesSyncParametersQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> DataSourcesSyncParameters:
        query = select(
            DataSourcesSyncState.current_page,
            DataSourcesSyncState.current_cutoff_date
        )
        try:
            result = (await session.execute(query)).mappings().one()
            return DataSourcesSyncParameters(
                page=result['current_page'],
                cutoff_date=result['current_cutoff_date']
            )
        except NoResultFound:
            # Add value
            state = DataSourcesSyncState()
            session.add(state)
            return DataSourcesSyncParameters(page=None, cutoff_date=None)
