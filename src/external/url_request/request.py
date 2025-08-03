"""Functions for making HTTP requests."""
from http import HTTPStatus

from aiohttp import ClientSession, ClientResponseError
from playwright.async_api import async_playwright
from tqdm.asyncio import tqdm

from src.external.url_request.constants import HTML_CONTENT_TYPE
from src.external.url_request.dtos.request_resources import RequestResources

from src.external.url_request.dtos.url_response import URLResponseInfo


async def execute_get(
    session: ClientSession,
    url: str
) -> URLResponseInfo:
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


async def get_response(session: ClientSession, url: str) -> URLResponseInfo:
    try:
        return await execute_get(session, url)
    except Exception as e:
        print(f"An error occurred while fetching {url}: {e}")
        return URLResponseInfo(success=False, exception=str(e))


async def make_simple_requests(urls: list[str]) -> list[URLResponseInfo]:
    async with ClientSession() as session:
        tasks = [get_response(session, url) for url in urls]
        results = await tqdm.gather(*tasks)
        return results


async def get_dynamic_html_content(
    rr: RequestResources,
    url: str
) -> URLResponseInfo | None:
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


async def fetch_and_render(
    rr: RequestResources,
    url: str
) -> URLResponseInfo | None:
    simple_response = await get_response(rr.session, url)
    if not simple_response.success:
        return simple_response

    if simple_response.content_type != HTML_CONTENT_TYPE:
        return simple_response

    return await get_dynamic_html_content(rr, url)


async def fetch_urls(urls: list[str]) -> list[URLResponseInfo]:
    async with ClientSession() as session:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            request_resources = RequestResources(session=session, browser=browser)
            tasks = [fetch_and_render(request_resources, url) for url in urls]
            results = await tqdm.gather(*tasks)
            return results
