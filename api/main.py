from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes.batch import batch_router
from api.routes.collector import collector_router
from api.routes.root import root_router
from collector_db.DatabaseClient import DatabaseClient
from core.CoreLogger import CoreLogger
from core.SourceCollectorCore import SourceCollectorCore


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize shared dependencies
    core_logger = CoreLogger()  # Replace with actual logger initialization
    db_client = DatabaseClient()  # Replace with actual DatabaseClient configuration
    source_collector_core = SourceCollectorCore(core_logger=core_logger, db_client=db_client)

    # Pass dependencies into the app state
    app.state.core = source_collector_core

    # Startup logic
    yield  # Code here runs before shutdown

    # Shutdown logic (if needed)
    app.state.core.shutdown()
    # Clean up resources, close connections, etc.
    pass


app = FastAPI(
    title="Source Collector API",
    description="API for collecting data sources",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(root_router)
app.include_router(collector_router)
app.include_router(batch_router)

# Dependency container
source_collector_core = None


def get_core(app: FastAPI) -> SourceCollectorCore:
    return app.state.core