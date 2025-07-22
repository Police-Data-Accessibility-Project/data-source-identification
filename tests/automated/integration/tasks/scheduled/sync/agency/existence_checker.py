from src.db.models.instantiations.agency.sqlalchemy import Agency
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo
from tests.automated.integration.tasks.scheduled.sync.agency.data import FIRST_CALL_RESPONSE, SECOND_CALL_RESPONSE


class AgencyChecker:
    """
    Checks if an agency matches expected values
    """

    def __init__(self):
        self.dict_ = {}
        for response in [FIRST_CALL_RESPONSE, SECOND_CALL_RESPONSE]:
            for agency in response.agencies:
                self.dict_[agency.agency_id] = agency

    def check(
        self,
        agency: Agency
    ):
        info: AgenciesSyncResponseInnerInfo = self.dict_.get(
            agency.agency_id
        )
        assert info.display_name == agency.name
        assert info.state_name == agency.state
        assert info.county_name == agency.county
        assert info.locality_name == agency.locality
        assert info.updated_at == agency.ds_last_updated_at