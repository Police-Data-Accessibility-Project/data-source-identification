from src.db.models.impl.agency.pydantic.upsert import AgencyUpsertModel
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo


def convert_agencies_sync_response_to_agencies_upsert(
    agencies: list[AgenciesSyncResponseInnerInfo]
) -> list[AgencyUpsertModel]:
    results = []
    for agency in agencies:
        results.append(
            AgencyUpsertModel(
                agency_id=agency.agency_id,
                name=agency.display_name,
                state=agency.state_name,
                county=agency.county_name,
                locality=agency.locality_name,
                ds_last_updated_at=agency.updated_at
            )
        )
    return results