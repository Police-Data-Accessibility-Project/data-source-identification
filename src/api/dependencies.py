from src.core.AsyncCore import AsyncCore
from src.core.SourceCollectorCore import SourceCollectorCore


def get_core() -> SourceCollectorCore:
    from src.api.main import app
    return app.state.core


def get_async_core() -> AsyncCore:
    from src.api.main import app
    return app.state.async_core