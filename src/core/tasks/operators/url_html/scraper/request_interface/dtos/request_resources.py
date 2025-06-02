import asyncio
from dataclasses import dataclass

from aiohttp import ClientSession
from playwright.async_api import async_playwright

from src.core.tasks.operators.url_html.scraper.request_interface.constants import MAX_CONCURRENCY


@dataclass
class RequestResources:
    session: ClientSession
    browser: async_playwright
    semaphore: asyncio.Semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
