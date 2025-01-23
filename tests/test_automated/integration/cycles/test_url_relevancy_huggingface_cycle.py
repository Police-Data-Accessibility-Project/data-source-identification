from unittest.mock import MagicMock

import pytest

from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.URLWithHTML import URLWithHTML
from collector_db.enums import ValidationStatus, ValidationSource
from collector_db.models import URLMetadata
from core.classes.URLRelevanceHuggingfaceCycler import URLRelevanceHuggingfaceCycler
from hugging_face.HuggingFaceInterface import HuggingFaceInterface


@pytest.mark.asyncio
async def test_url_relevancy_huggingface_cycle(db_data_creator):
    batch_id = db_data_creator.batch()
    url_mappings = db_data_creator.urls(batch_id=batch_id, url_count=3).url_mappings
    url_ids = [url_info.url_id for url_info in url_mappings]
    await db_data_creator.html_data(url_ids)
    await db_data_creator.metadata([url_ids[0]])

    def num_to_bool(num: int) -> bool:
        if num == 0:
            return True
        else:
            return False

    def mock_get_url_relevancy(
        urls_with_html: list[URLWithHTML],
        threshold: float = 0.8
    ) -> list[bool]:
        results = []
        for url_with_html in urls_with_html:
            num = url_with_html.url_id % 2
            results.append(num_to_bool(num))

        return results

    mock_hf_interface = MagicMock(spec=HuggingFaceInterface)
    mock_hf_interface.get_url_relevancy = mock_get_url_relevancy

    cycler = URLRelevanceHuggingfaceCycler(
        adb_client=AsyncDatabaseClient(),
        huggingface_interface=mock_hf_interface
    )
    await cycler.cycle()

    results = await db_data_creator.adb_client.get_all(URLMetadata)

    assert len(results) == 3
    for result in results:
        assert result.url_id in url_ids
        assert result.value in ['True', 'False']
        assert result.validation_status == ValidationStatus.PENDING_VALIDATION.value
        assert result.validation_source == ValidationSource.MACHINE_LEARNING.value