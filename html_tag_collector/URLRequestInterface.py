PYPPETEER_CHROMIUM_REVISION = '1263111'
# This is needed in order to render javascript
# (the arender method uses Pypeteer under the hood)
import os
os.environ['PYPPETEER_CHROMIUM_REVISION'] = PYPPETEER_CHROMIUM_REVISION
from dataclasses import dataclass

from datasets import tqdm
from requests import Response
from requests_html import AsyncHTMLSession

from html_tag_collector.constants import USER_AGENT


@dataclass
class URLResponseInfo:
    success: bool
    response: Response or Exception

class URLRequestInterface:

    def __init__(self):
        self.session = AsyncHTMLSession(workers=100, browser_args=["--no-sandbox", f"--user-agent={USER_AGENT}"])

    async def get_response(self, url: str):
        try:
            response = await self.session.get(url)
        except Exception as e:
            response = e
        return response

    async def fetch(self, url: str):
        response = await self.get_response(url)
        return response

    async def fetch_and_render(self, url: str):
        response = await self.get_response(url)
        if isinstance(response, Exception):
            return response
        await response.html.arender(timeout=10, sleep=2)
        return response

    async def fetch_urls(self, urls: list[str], render_javascript: bool):
        if render_javascript:
            tasks = [self.fetch_and_render(url) for url in urls]
        else:
            tasks = [self.fetch(url) for url in urls]

        return await tqdm.gather(*tasks)

    async def process_results(self, results) -> list[URLResponseInfo]:
        uris = []
        for result in results:
            if isinstance(result, Exception):
                uris.append(URLResponseInfo(success=False, response=result))
            else:
                uris.append(URLResponseInfo(success=True, response=result))
        return uris

    async def make_requests(
            self,
            urls: list[str],
            render_javascript: bool = False
    ) -> list[URLResponseInfo]:
        try:
            results = await self.fetch_urls(urls, render_javascript)
        except Exception as e:
            print(f"An error occurred while making the requests: {e}")
            results = []
        finally:
            await self.session.close()
            return await self.process_results(results)


