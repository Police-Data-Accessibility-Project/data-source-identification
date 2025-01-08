from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes.batch import batch_router
from api.routes.collector import collector_router
from api.routes.label_studio import label_studio_router
from api.routes.root import root_router
from collector_db.DatabaseClient import DatabaseClient
from core.CoreLogger import CoreLogger
from core.SourceCollectorCore import SourceCollectorCore
from util.helper_functions import get_from_env


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize shared dependencies
    db_client = DatabaseClient()
    await setup_database(db_client)
    source_collector_core = SourceCollectorCore(
        core_logger=CoreLogger(
            db_client=db_client
        ),
        db_client=DatabaseClient(),
    )

    # Pass dependencies into the app state
    app.state.core = source_collector_core

    # Startup logic
    yield  # Code here runs before shutdown

    # Shutdown logic (if needed)
    app.state.core.shutdown()
    # Clean up resources, close connections, etc.
    pass


async def setup_database(db_client):
    # Initialize database if dev environment, otherwise apply migrations
    try:
        get_from_env("DEV")
        db_client.init_db()
    except Exception as e:
        return


app = FastAPI(
    title="Source Collector API",
    description="API for collecting data sources",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(root_router)
app.include_router(collector_router)
app.include_router(batch_router)
app.include_router(label_studio_router)
