


def format_agency_ids_result(agency_ids: list[int | None]) -> list[int]:
    if agency_ids == [None]:
        return []
    return agency_ids