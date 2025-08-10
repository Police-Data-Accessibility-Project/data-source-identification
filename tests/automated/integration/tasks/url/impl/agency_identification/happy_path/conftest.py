from unittest.mock import create_autospec, AsyncMock

import pytest

from src.collectors.source_collectors.muckrock.api_interface.core import MuckrockAPIInterface
from src.core.tasks.url.operators.agency_identification.core import AgencyIdentificationTaskOperator
from src.core.tasks.url.operators.agency_identification.subtasks.loader import AgencyIdentificationSubtaskLoader
from src.db.client.async_ import AsyncDatabaseClient
from src.external.pdap.client import PDAPClient
from tests.automated.integration.tasks.url.impl.agency_identification.happy_path.mock import mock_run_subtask


@pytest.fixture
def operator(
    adb_client_test: AsyncDatabaseClient
):

    operator = AgencyIdentificationTaskOperator(
        adb_client=adb_client_test,
        loader=AgencyIdentificationSubtaskLoader(
            pdap_client=create_autospec(PDAPClient),
            muckrock_api_interface=create_autospec(MuckrockAPIInterface)
        )
    )
    operator.run_subtask = AsyncMock(
        side_effect=mock_run_subtask
    )

    return operator
