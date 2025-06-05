from contextlib import asynccontextmanager

import aiohttp
import uvicorn
from discord_poster import DiscordPoster
from fastapi import FastAPI
from pdap_access_manager import AccessManager
from starlette.responses import RedirectResponse

from src.api.endpoints.annotate.routes import annotate_router
from src.api.endpoints.batch.routes import batch_router
from src.api.endpoints.collector.routes import collector_router
from src.api.endpoints.metrics.routes import metrics_router
from src.api.endpoints.review.routes import review_router
from src.api.endpoints.root import root_router
from src.api.endpoints.search.routes import search_router
from src.api.endpoints.task.routes import task_router
from src.api.endpoints.url.routes import url_router
from src.collectors.manager import AsyncCollectorManager
from src.collectors.source_collectors.muckrock.api_interface.core import MuckrockAPIInterface
from src.core.core import AsyncCore
from src.core.logger import AsyncCoreLogger
from src.core.env_var_manager import EnvVarManager
from src.core.scheduled_task_manager import AsyncScheduledTaskManager
from src.core.tasks.manager import TaskManager
from src.core.tasks.operators.url_html.scraper.parser.core import HTMLResponseParser
from src.core.tasks.operators.url_html.scraper.request_interface.core import URLRequestInterface
from src.db.client.async_ import AsyncDatabaseClient
from src.db.client.sync import DatabaseClient
from src.core.tasks.operators.url_html.scraper.root_url_cache.core import RootURLCache
from src.pdap_api.client import PDAPClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    env_var_manager = EnvVarManager.get()

    # Initialize shared dependencies
    db_client = DatabaseClient(
        db_url=env_var_manager.get_postgres_connection_string()
    )
    adb_client = AsyncDatabaseClient(
        db_url=env_var_manager.get_postgres_connection_string(is_async=True)
    )
    await setup_database(db_client)
    core_logger = AsyncCoreLogger(adb_client=adb_client)

    session = aiohttp.ClientSession()

    task_manager = TaskManager(
        adb_client=adb_client,
        url_request_interface=URLRequestInterface(),
        html_parser=HTMLResponseParser(
            root_url_cache=RootURLCache()
        ),
        discord_poster=DiscordPoster(
            webhook_url=env_var_manager.discord_webhook_url
        ),
        pdap_client=PDAPClient(
            access_manager=AccessManager(
                email=env_var_manager.pdap_email,
                password=env_var_manager.pdap_password,
                api_key=env_var_manager.pdap_api_key,
                session=session
            )
        ),
        muckrock_api_interface=MuckrockAPIInterface(
            session=session
        )
    )
    async_collector_manager = AsyncCollectorManager(
        logger=core_logger,
        adb_client=adb_client,
        post_collection_function_trigger=task_manager.task_trigger
    )

    async_core = AsyncCore(
        adb_client=adb_client,
        task_manager=task_manager,
        collector_manager=async_collector_manager
    )
    async_scheduled_task_manager = AsyncScheduledTaskManager(async_core=async_core)

    # Pass dependencies into the app state
    app.state.async_core = async_core
    app.state.async_scheduled_task_manager = async_scheduled_task_manager
    app.state.logger = core_logger

    # Startup logic
    yield  # Code here runs before shutdown

    # Shutdown logic (if needed)
    # Clean up resources, close connections, etc.
    await core_logger.shutdown()
    await async_core.shutdown()
    await session.close()
    pass


async def setup_database(db_client):
    # Initialize database if dev environment, otherwise apply migrations
    try:
        db_client.init_db()
    except Exception as e:
        return


app = FastAPI(
    title="Source Collector API",
    description="API for collecting data sources",
    docs_url='/api',
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/docs", include_in_schema=False)
async def redirect_docs():
    return RedirectResponse(url="/api")


routers = [
    root_router,
    collector_router,
    batch_router,
    annotate_router,
    url_router,
    task_router,
    review_router,
    search_router,
    metrics_router
]

for router in routers:
    app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)