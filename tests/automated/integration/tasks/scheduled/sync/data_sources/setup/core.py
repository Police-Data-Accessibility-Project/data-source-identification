from contextlib import contextmanager
from unittest.mock import patch

from src.external.pdap.client import PDAPClient


@contextmanager
def patch_sync_data_sources(side_effects: list):
    with patch.object(
        PDAPClient,
        "sync_data_sources",
        side_effect=side_effects
    ):
        yield