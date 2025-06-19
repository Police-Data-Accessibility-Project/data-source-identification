from datetime import datetime

from src.pdap_api.dtos.agencies_sync import AgenciesSyncResponseInfo, AgenciesSyncResponseInnerInfo

PREEXISTING_AGENCY_1 = AgenciesSyncResponseInnerInfo(
    display_name="Preexisting Agency 1",
    agency_id=1,
    state_name="CA",
    county_name="San Francisco",
    locality_name="San Francisco",
    updated_at=datetime(2023, 1, 1, 0, 0, 0)
)

PREEXISTING_AGENCY_2 = AgenciesSyncResponseInnerInfo(
    display_name="Preexisting Agency 2",
    agency_id=2,
    state_name="NC",
    county_name="NC County",
    locality_name="NC City",
    updated_at=datetime(2025, 10, 17, 3, 0, 0)
)

PREEXISTING_AGENCIES = [
    PREEXISTING_AGENCY_1,
    PREEXISTING_AGENCY_2
]

FIRST_CALL_RESPONSE = AgenciesSyncResponseInfo(
    agencies=[
        AgenciesSyncResponseInnerInfo(
            display_name="New Agency 1",
            agency_id=1,
            state_name=None,
            county_name=None,
            locality_name=None,
            updated_at=datetime(2022, 3, 5, 7, 6, 9)
        ),
        AgenciesSyncResponseInnerInfo(
            display_name="New Agency 2",
            agency_id=2,
            state_name="Ohio",
            county_name=None,
            locality_name=None,
            updated_at=datetime(2024, 9, 5, 7, 6, 9)
        ),
        AgenciesSyncResponseInnerInfo(
            display_name="New Agency 3",
            agency_id=1,
            state_name="AL",
            county_name="AL County",
            locality_name=None,
            updated_at=datetime(2023, 12, 4, 0, 0, 0)
        ),
        AgenciesSyncResponseInnerInfo(
            display_name="Test Agency 2",
            agency_id=2,
            state_name="TX",
            county_name="TX County",
            locality_name="TX City",
            updated_at=datetime(2021, 1, 1, 0, 0, 0)
        ),
        PREEXISTING_AGENCY_1
    ],
)

SECOND_CALL_RESPONSE = AgenciesSyncResponseInfo(
    agencies=[
        PREEXISTING_AGENCY_2
    ]
)

THIRD_CALL_RESPONSE = AgenciesSyncResponseInfo(
    agencies=[]
)

AGENCIES_SYNC_RESPONSES = [
    FIRST_CALL_RESPONSE,
    SECOND_CALL_RESPONSE,
    THIRD_CALL_RESPONSE
]