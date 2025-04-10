from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api.routes.annotate import annotate_router
from api.routes.batch import batch_router
from api.routes.collector import collector_router
from api.routes.review import review_router
from api.routes.root import root_router
from api.routes.task import task_router
from api.routes.url import url_router
from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DatabaseClient import DatabaseClient
from core.AsyncCore import AsyncCore
from core.CoreLogger import CoreLogger
from core.ScheduledTaskManager import AsyncScheduledTaskManager
from core.SourceCollectorCore import SourceCollectorCore
from html_tag_collector.ResponseParser import HTMLResponseParser
from html_tag_collector.RootURLCache import RootURLCache
from html_tag_collector.URLRequestInterface import URLRequestInterface
from hugging_face.HuggingFaceInterface import HuggingFaceInterface
from util.DiscordNotifier import DiscordPoster
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
    async_core = AsyncCore(
        adb_client=AsyncDatabaseClient(),
        huggingface_interface=HuggingFaceInterface(),
        url_request_interface=URLRequestInterface(),
        html_parser=HTMLResponseParser(
            root_url_cache=RootURLCache()
        ),
        discord_poster=DiscordPoster(
            webhook_url=get_from_env("DISCORD_WEBHOOK_URL")
        )
    )
    async_scheduled_task_manager = AsyncScheduledTaskManager(async_core=async_core)

    # Pass dependencies into the app state
    app.state.core = source_collector_core
    app.state.async_core = async_core
    app.state.async_scheduled_task_manager = async_scheduled_task_manager

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

routers = [
    root_router,
    collector_router,
    batch_router,
    annotate_router,
    url_router,
    task_router,
    review_router
]

for router in routers:
    app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)