from unittest.mock import MagicMock

from collector_db.DTOs.InsertURLsInfo import InsertURLsInfo
from core.DTOs.LabelStudioExportResponseInfo import LabelStudioExportResponseInfo
from label_studio_interface.DTOs.LabelStudioTaskExportInfo import LabelStudioTaskExportInfo
from label_studio_interface.LabelStudioAPIManager import LabelStudioAPIManager
from tests.test_automated.integration.api.conftest import APITestHelper


def test_export_batch_to_label_studio(
    api_test_helper: APITestHelper,
):
    ath = api_test_helper
    mock_lsam = MagicMock(spec=LabelStudioAPIManager)
    mock_lsam.export_tasks_into_project.return_value = 123
    ath.core.label_studio_api_manager = mock_lsam
    batch = ath.db_data_creator.batch()
    iui: InsertURLsInfo = ath.db_data_creator.urls(batch_id=batch, url_count=10)
    response: LabelStudioExportResponseInfo = ath.request_validator.export_batch_to_label_studio(
        batch_id=batch
    )

    assert response.label_studio_import_id == 123
    assert response.num_urls_imported == 10

    # Reconstruct the data that was sent to the LSAM
    data = []
    for mapping in iui.url_mappings:
        data.append(LabelStudioTaskExportInfo(url=mapping.url))

    mock_lsam.export_tasks_into_project.assert_called_once_with(
        data=data
    )
