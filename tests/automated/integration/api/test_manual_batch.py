
import pytest

from src.api.endpoints.collector.dtos.manual_batch.post import ManualBatchInnerInputDTO, ManualBatchInputDTO
from src.db.models.instantiations.link.batch_url import LinkBatchURL
from src.db.models.instantiations.url.optional_data_source_metadata import URLOptionalDataSourceMetadata
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.instantiations.batch.sqlalchemy import Batch
from src.collectors.enums import CollectorType
from src.core.enums import RecordType


@pytest.mark.asyncio
async def test_manual_batch(api_test_helper):
    ath = api_test_helper

    manual_batch_name = "test_manual_batch"

    # Create 50 entries with just URL
    dtos = []
    for i in range(50):
        dto = ManualBatchInnerInputDTO(
            url=f"https://example.com/{i}",
        )
        dtos.append(dto)

    # Create 50 entries with URL and all optional fields
    for i in range(50):
        dto = ManualBatchInnerInputDTO(
            url=f"https://example.com/{i+50}",
            name=manual_batch_name,
            description=f"Description {i}",
            collector_metadata={
                "name": f"Name {i}",
            },
            record_type=RecordType.ARREST_RECORDS,
            record_formats=[f"Record Format {i}"],
            data_portal_type=f"Data Portal Type {i}",
            supplying_entity=f"Supplying Entity {i}"
        )
        dtos.append(dto)

    input_dto = ManualBatchInputDTO(
        name=manual_batch_name,
        entries=dtos
    )

    # Submit batch successfully
    response = await ath.request_validator.submit_manual_batch(input_dto)

    # Check 100 URLs in url attribute
    assert len(response.urls) == 100

    # Get batch from database
    adb_client = ath.adb_client()
    batches = await adb_client.get_all(Batch)

    # Confirm only one batch
    assert len(batches) == 1

    batch: Batch = batches[0]
    # Assert batch id matches response's batch id
    assert batch.id == response.batch_id
    # Assert strategy of manual
    assert batch.strategy == CollectorType.MANUAL.value
    # Assert parameters has name value of `test_manual_batch`
    assert batch.parameters["name"] == manual_batch_name
    # Assert has expected user id
    assert batch.user_id == 1

    # Get URLs from database
    urls: list[URL] = await adb_client.get_all(URL)
    links: list[LinkBatchURL] = await adb_client.get_all(LinkBatchURL)

    # Confirm 100 URLs
    assert len(urls) == 100

    def check_attributes(
            object: URL or URLOptionalDataSourceMetadata,
            attributes: list[str],
            attributes_are_none: bool
    ):
        for attr in attributes:
            if attributes_are_none:
                if getattr(object, attr) is not None:
                    return False
            else:
                if getattr(object, attr) is None:
                    return False
        return True

    def check_link(link: LinkBatchURL):
        assert link.batch_id == batch.id

    def check_url(url: URL, url_only: bool):
        assert url.url is not None
        other_attributes = ["name", "description", "collector_metadata", "record_type"]
        return check_attributes(url, other_attributes, url_only)


    # Confirm 50 have only name value
    count_only_name = 0
    for url in urls:
        if check_url(url, True):
            count_only_name += 1
    for link in links:
        check_link(link)
    assert count_only_name == 50
    # Confirm 50 have all optional fields
    count_all = 0
    for url in urls:
        if check_url(url, False):
            count_all += 1
    assert count_all == 50

    # Get Optional URL Metadata from Database
    opt_metadata: list[URLOptionalDataSourceMetadata] = await adb_client.get_all(URLOptionalDataSourceMetadata)

    # Confirm 100
    assert len(opt_metadata) == 100

    def check_opt_metadata(metadata: URLOptionalDataSourceMetadata, no_optional: bool):
        assert metadata.url_id is not None
        other_attributes = ["record_formats", "data_portal_type", "supplying_entity"]
        return check_attributes(metadata, other_attributes, no_optional)

    # Confirm 50 have nothing but URL id
    count_only_url_id = 0
    for metadata in opt_metadata:
        if check_opt_metadata(metadata, True):
            count_only_url_id += 1
    assert count_only_url_id == 50

    # Confirm 50 have all optional fields
    count_all = 0
    for metadata in opt_metadata:
        if check_opt_metadata(metadata, False):
            count_all += 1
    assert count_all == 50

    # Insert another batch including good urls and one duplicate
    more_dtos = []
    for i in range(49):
        dto = ManualBatchInnerInputDTO(
            url=f"https://example.com/{i+100}",
        )
        more_dtos.append(dto)

    for i in range(2):
        dto = ManualBatchInnerInputDTO(
            url=f"https://example.com/{i+1}",
        )
        more_dtos.append(dto)


    duplicate_input_dto = ManualBatchInputDTO(
        name=manual_batch_name,
        entries=more_dtos
    )

    # Submit batch
    response = await ath.request_validator.submit_manual_batch(duplicate_input_dto)
    # Check duplicate URLs
    assert len(response.duplicate_urls) == 2
    assert response.duplicate_urls == ['https://example.com/1', 'https://example.com/2']
    assert len(response.urls) == 49

    # Check 149 URLs in database
    urls: list[URL] = await adb_client.get_all(URL)
    assert len(urls) == 149
