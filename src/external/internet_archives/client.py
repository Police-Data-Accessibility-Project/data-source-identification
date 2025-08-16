import asyncio
from asyncio import Semaphore

from aiolimiter import AsyncLimiter
from aiohttp import ClientSession

from src.external.internet_archives.convert import convert_capture_to_archive_metadata
from src.external.internet_archives.models.capture import IACapture
from src.external.internet_archives.models.ia_url_mapping import InternetArchivesURLMapping

limiter = AsyncLimiter(
    max_rate=50,
    time_period=50
)
sem = Semaphore(10)

class InternetArchivesClient:

    def __init__(
        self,
        session: ClientSession
    ):
        self.session = session

    async def _get_url_snapshot(self, url: str) -> IACapture | None:
        params = {
            "url": url,
            "output": "json",
            "limit": "1",
            "gzip": "false",
            "filter": "statuscode:200",
            "fl": "timestamp,original,length,digest"
        }
        async with sem:
            async with limiter:
                async with self.session.get(
                    f"http://web.archive.org/cdx/search/cdx",
                    params=params
                ) as response:
                    raw_data = await response.json()
                    if len(raw_data) == 0:
                        return None
                    fields = raw_data[0]
                    values = raw_data[1]
                    d = dict(zip(fields, values))

                    return IACapture(**d)

    async def search_for_url_snapshot(self, url: str) -> InternetArchivesURLMapping:
        try:
            capture: IACapture | None = await self._get_url_snapshot(url)
        except Exception as e:
            return InternetArchivesURLMapping(
                url=url,
                ia_metadata=None,
                error=f"{e.__class__.__name__}: {e}"
            )

        if capture is None:
            return InternetArchivesURLMapping(
                url=url,
                ia_metadata=None,
                error=None
            )

        metadata = convert_capture_to_archive_metadata(capture)
        return InternetArchivesURLMapping(
            url=url,
            ia_metadata=metadata,
            error=None
        )
