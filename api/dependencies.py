from src.core.AsyncCore import AsyncCore
from src.core.SourceCollectorCore import SourceCollectorCore


def get_core() -> SourceCollectorCore:
    from api.main import app
    return app.state.core


def get_async_core() -> AsyncCore:
    from api.main import app
    return app.state.async_core