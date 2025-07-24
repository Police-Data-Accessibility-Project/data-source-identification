from sqlalchemy import select

from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.instantiations.agency.sqlalchemy import Agency
from tests.automated.integration.tasks.scheduled.sync.data_sources.setup.enums import AgencyAssigned


class AgencyAssignmentManager:

    def __init__(self, adb_client: AsyncDatabaseClient):
        self.adb_client = adb_client
        self._dict: dict[AgencyAssigned, int] = {}

    async def setup(self):
        agencies = []
        for ag_enum in AgencyAssigned:
            agency = Agency(
                agency_id=ag_enum.value,
                name=f"Test Agency {ag_enum.name}",
                state="test_state",
                county="test_county",
                locality="test_locality"
            )
            agencies.append(agency)
        await self.adb_client.add_all(agencies)
        agency_ids = await self.adb_client.scalars(select(Agency.agency_id))
        for ag_enum, agency_id in zip(AgencyAssigned, agency_ids):
            self._dict[ag_enum] = agency_id

    async def get(self, ag_enum: AgencyAssigned) -> int:
        return self._dict[ag_enum]
