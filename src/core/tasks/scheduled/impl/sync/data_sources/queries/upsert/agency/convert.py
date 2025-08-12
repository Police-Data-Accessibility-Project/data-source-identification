from src.db.models.impl.link.url_agency.pydantic import LinkURLAgencyPydantic


def convert_to_link_url_agency_models(
    url_id: int,
    agency_ids: list[int]
) -> list[LinkURLAgencyPydantic]:
    return [
        LinkURLAgencyPydantic(
            url_id=url_id,
            agency_id=agency_id
        )
        for agency_id in agency_ids
    ]