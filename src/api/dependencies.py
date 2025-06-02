from src.core.core import AsyncCore


def get_async_core() -> AsyncCore:
    from src.api.main import app
    return app.state.async_core