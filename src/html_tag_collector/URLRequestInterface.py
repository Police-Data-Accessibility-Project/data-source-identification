import asyncio
from http import HTTPStatus
from typing import Optional

from aiohttp import ClientSession, ClientResponseError
from playwright.async_api import async_playwright

from dataclasses import dataclass

from pydantic import BaseModel
from tqdm.asyncio import tqdm

MAX_CONCURRENCY = 5

class URLResponseInfo(BaseModel):
    success: bool
    status: Optional[HTTPStatus] = None
    html: Optional[str] = None
    content_type: Optional[str] = None
    exception: Optional[str] = None


@dataclass
class RequestResources:
    session: ClientSession
    browser: async_playwright
    semaphore: asyncio.Semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

HTML_CONTENT_TYPE = "text/html"

class URLRequestInterface:

    async def get_response(self, session: ClientSession, url: str) -> URLResponseInfo:
        try:
            async with session.get(url, timeout=20) as response:
                response.raise_for_status()
                text = await response.text()
                return URLResponseInfo(
                    success=True,
                    html=text,
                    content_type=response.headers.get("content-type"),
                    status=HTTPStatus(response.status)
                )
        except ClientResponseError as e:
            return URLResponseInfo(success=False, status=HTTPStatus(e.status), exception=str(e))
        except Exception as e:
            print(f"An error occurred while fetching {url}: {e}")
            return URLResponseInfo(success=False, exception=str(e))

    async def fetch_and_render(self, rr: RequestResources, url: str) -> Optional[URLResponseInfo]:
        simple_response = await self.get_response(rr.session, url)
        if not simple_response.success:
            return simple_response

        if simple_response.content_type != HTML_CONTENT_TYPE:
            return simple_response

        await self.get_dynamic_html_content(rr, url)

    async def get_dynamic_html_content(self, rr, url):
        # For HTML responses, attempt to load the page to check for dynamic html content
        async with rr.semaphore:
            page = await rr.browser.new_page()
            try:
                await page.goto(url)
                await page.wait_for_load_state("networkidle")
                html_content = await page.content()
                return URLResponseInfo(
                    success=True,
                    html=html_content,
                    content_type=HTML_CONTENT_TYPE,
                    status=HTTPStatus.OK
                )
            except Exception as e:
                return URLResponseInfo(success=False, exception=str(e))
            finally:
                await page.close()

    async def fetch_urls(self, urls: list[str]) -> list[URLResponseInfo]:
        async with ClientSession() as session:
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(headless=True)
                request_resources = RequestResources(session=session, browser=browser)
                tasks = [self.fetch_and_render(request_resources, url) for url in urls]
                results = await tqdm.gather(*tasks)
                return results

    async def make_requests_with_html(
            self,
            urls: list[str],
    ) -> list[URLResponseInfo]:
        return await self.fetch_urls(urls)

    async def make_simple_requests(self, urls: list[str]) -> list[URLResponseInfo]:
        async with ClientSession() as session:
            tasks = [self.get_response(session, url) for url in urls]
            results = await tqdm.gather(*tasks)
            return results



