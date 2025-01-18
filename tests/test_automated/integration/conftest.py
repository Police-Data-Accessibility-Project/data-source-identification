
import pytest

from core.CoreLogger import CoreLogger
from core.SourceCollectorCore import SourceCollectorCore


@pytest.fixture
def test_core(db_client_test):
    with CoreLogger(
        db_client=db_client_test
    ) as logger:
        core = SourceCollectorCore(
            db_client=db_client_test,
            core_logger=logger,
            dev_mode=True
        )
        yield core
        core.shutdown()

