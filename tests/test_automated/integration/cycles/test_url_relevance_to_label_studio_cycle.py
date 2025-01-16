from unittest.mock import MagicMock

import pytest

from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.enums import URLMetadataAttributeType, ValidationStatus
from core.classes.URLRelevanceToLabelStudioCycler import URLRelevanceToLabelStudioCycler
from label_studio_interface.DTOs.LabelStudioTaskExportInfo import LabelStudioTaskExportInfo
from label_studio_interface.LabelStudioAPIManager import LabelStudioAPIManager

@pytest.mark.asyncio
async def test_url_relevance_to_label_studio_cycle(db_data_creator):
    batch_id = db_data_creator.batch()
    url_mappings = db_data_creator.urls(batch_id=batch_id, url_count=3).url_mappings
    url_ids = [url_info.url_id for url_info in url_mappings]
    await db_data_creator.html_data(url_ids)
    await db_data_creator.metadata(
        url_ids=url_ids,
        attribute=URLMetadataAttributeType.RELEVANT,
        validation_status=ValidationStatus.PENDING_VALIDATION,
    )

    def mock_export_tasks_into_project(
            data: list[LabelStudioTaskExportInfo]
    ) -> list[int]:
        count = len(data)
        return [i for i in range(count)]


    mock_label_studio_api_manager = MagicMock(spec=LabelStudioAPIManager)
    mock_label_studio_api_manager.export_tasks_into_project = mock_export_tasks_into_project

    cycler = URLRelevanceToLabelStudioCycler(
        adb_client=AsyncDatabaseClient(),
        label_studio_api_manager=mock_label_studio_api_manager
    )

    await cycler.cycle()

    # TODO: Confirm tasks present in `label_studio_tasks`

    # TODO: Confirm metadata updated