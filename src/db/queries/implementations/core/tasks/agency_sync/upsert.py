from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.db.models.instantiations.sync_state_agencies import AgenciesSyncState
from src.pdap_api.dtos.agencies_sync import AgenciesSyncResponseInnerInfo


def get_upsert_agencies_query(
    agencies: list[AgenciesSyncResponseInnerInfo]
):
    agency_dicts = {}
    for agency in agencies:
        agency_dict = {
            'agency_id': agency.agency_id,
            'name': agency.display_name,
            'state': agency.state_name,
            'county': agency.county_name,
            'locality': agency.locality_name,
            'updated_at': agency.updated_at
        }
        agency_dicts[agency.pdap_agency_id] = agency_dict

    stmt = (
        pg_insert(AgenciesSyncState)
        .values(agency_dicts)
    )

    stmt = stmt.on_conflict_do_update(
        index_elements=['agency_id'],
        set_={
            'name': stmt.excluded.name,
            'state': stmt.excluded.state,
            'county': stmt.excluded.county,
            'locality': stmt.excluded.locality,
            'updated_at': stmt.excluded.updated_at
        }
    )

    return stmt