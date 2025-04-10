import asyncio
from typing import Optional

from aiohttp import ClientSession
from playwright.async_api import async_playwright

from dataclasses import dataclass

from tqdm.asyncio import tqdm

MAX_CONCURRENCY = 5

@dataclass
class URLResponseInfo:
    success: bool
    html: Optional[str] = None
    content_type: Optional[str] = None
    exception: Optional[Exception] = None

@dataclass
class RequestResources:
    session: ClientSession
    browser: async_playwright
    semaphore: asyncio.Semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

def ensure_browsers_installed():
    # TODO: Slated for destruction
    pass

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
                    content_type=response.headers.get("content-type")
                )
        except Exception as e:
            print(f"An error occurred while fetching {url}: {e}")
            return URLResponseInfo(success=False, exception=e)

    async def fetch_and_render(self, rr: RequestResources, url: str) -> URLResponseInfo:
        print(f"Fetch and Rendering {url}")
        simple_response = await self.get_response(rr.session, url)
        if not simple_response.success:
            return simple_response

        if simple_response.content_type != HTML_CONTENT_TYPE:
            return simple_response

        # For HTML responses, attempt to load the page to check for dynamic html content
        async with rr.semaphore:
            page = await rr.browser.new_page()
            try:
                await page.goto(url)
                await page.wait_for_load_state("networkidle")
                html_content = await page.content()
                return URLResponseInfo(success=True, html=html_content, content_type=HTML_CONTENT_TYPE)
            except Exception as e:
                return URLResponseInfo(success=False, exception=e)
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

    async def make_requests(
            self,
            urls: list[str],
    ) -> list[URLResponseInfo]:
        ensure_browsers_installed()
        return await self.fetch_urls(urls)



