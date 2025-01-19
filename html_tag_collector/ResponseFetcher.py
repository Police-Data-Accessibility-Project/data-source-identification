import ssl
import traceback
from dataclasses import dataclass
from typing import Optional

import requests
import urllib3
from requests_html import AsyncHTMLSession

from html_tag_collector.constants import REQUEST_HEADERS
from html_tag_collector.url_adjustment_functions import http_to_https


@dataclass
class ResponseInfo:
    url: str
    response: Optional[requests.Response]

class ResponseFetcher:

    def __init__(self, session: AsyncHTMLSession, url: str, debug=False):
        self.headers = REQUEST_HEADERS
        self.session = session
        self.url = url
        self.debug = debug

    def debug_print(self, s: str):
        if self.debug:
            print(s)

    async def fetch(self, verify_ssl=True):
        return await self.session.get(
            self.url,
            headers=self.headers,
            timeout=120,
            verify=verify_ssl
        )

    async def get_response(self):
        response = None
        try:
            response = await self.fetch()
        except (requests.exceptions.SSLError, ssl.SSLError):
            # This error is raised when the website uses a legacy SSL version, which is not supported by requests
            self.debug_print(f"SSLError: {self.url}")

            # Retry without SSL verification
            response = await self.fetch(verify_ssl=False)
        except requests.exceptions.ConnectionError:
            # Sometimes this error is raised because the provided url uses http
            # when it should be https and the website does not handle it properly
            self.debug_print(f"MaxRetryError: {self.url}")

            response = await self.retry_with_https()
        except (urllib3.exceptions.LocationParseError, requests.exceptions.ReadTimeout) as e:
            self.debug_print(f"{type(e).__name__}: {self.url}")
        except Exception as e:
            self.debug_print(f"""
                "Exception:", {self.url}
                {traceback.format_exc()}
                {e}
            """)
        finally:
            self.debug_print(f"{self.url} - {str(response)}")
            return response

    async def retry_with_https(self):
        self.url = http_to_https(self.url)
        return await self.fetch()
