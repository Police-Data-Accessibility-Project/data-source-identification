from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync.agency.dtos.parameters import AgencySyncParameters
from src.db.models.instantiations.state.sync.agencies import AgenciesSyncState
from src.db.queries.base.builder import QueryBuilderBase


class GetAgenciesSyncParametersQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> AgencySyncParameters:
        query = select(
            AgenciesSyncState.current_page,
            AgenciesSyncState.current_cutoff_date
        )
        try:
            result = (await session.execute(query)).mappings().one()
            return AgencySyncParameters(
                page=result['current_page'],
                cutoff_date=result['current_cutoff_date']
            )
        except NoResultFound:
            # Add value
            state = AgenciesSyncState()
            session.add(state)
            return AgencySyncParameters(page=None, cutoff_date=None)



