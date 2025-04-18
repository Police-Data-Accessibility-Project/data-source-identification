import asyncio
from contextlib import asynccontextmanager

import aiohttp
import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from api.routes.annotate import annotate_router
from api.routes.batch import batch_router
from api.routes.collector import collector_router
from api.routes.review import review_router
from api.routes.root import root_router
from api.routes.task import task_router
from api.routes.url import url_router
from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DatabaseClient import DatabaseClient
from collector_manager.AsyncCollectorManager import AsyncCollectorManager
from core.AsyncCore import AsyncCore
from core.AsyncCoreLogger import AsyncCoreLogger
from core.EnvVarManager import EnvVarManager
from core.ScheduledTaskManager import AsyncScheduledTaskManager
from core.SourceCollectorCore import SourceCollectorCore
from core.TaskManager import TaskManager
from html_tag_collector.ResponseParser import HTMLResponseParser
from html_tag_collector.RootURLCache import RootURLCache
from html_tag_collector.URLRequestInterface import URLRequestInterface
from hugging_face.HuggingFaceInterface import HuggingFaceInterface
from pdap_api_client.AccessManager import AccessManager
from pdap_api_client.PDAPClient import PDAPClient
from util.DiscordNotifier import DiscordPoster



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

    source_collector_core = SourceCollectorCore(
        db_client=DatabaseClient(),
    )
    task_manager = TaskManager(
        adb_client=adb_client,
        huggingface_interface=HuggingFaceInterface(),
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
    app.state.core = source_collector_core
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
    review_router
]

for router in routers:
    app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)