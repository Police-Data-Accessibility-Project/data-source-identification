from src.pdap_api.dtos.agencies_sync import AgenciesSyncResponseInnerInfo


def get_upsert_agencies_mappings(
    agencies: list[AgenciesSyncResponseInnerInfo]
) -> list[dict]:
    agency_dicts = []
    for agency in agencies:
        agency_dict = {
            'agency_id': agency.agency_id,
            'name': agency.display_name,
            'state': agency.state_name,
            'county': agency.county_name,
            'locality': agency.locality_name,
            'ds_last_updated_at': agency.updated_at
        }
        agency_dicts.append(agency_dict)

    return agency_dicts