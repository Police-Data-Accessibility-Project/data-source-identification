from core.SourceCollectorCore import SourceCollectorCore


def get_core() -> SourceCollectorCore:
    from api.main import app
    return app.state.core
