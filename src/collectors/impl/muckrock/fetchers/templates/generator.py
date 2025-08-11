from src.collectors.impl.muckrock.fetchers.templates.iter_fetcher import MuckrockIterFetcherBase
from src.collectors.impl.muckrock.exceptions import RequestFailureException


class MuckrockGeneratorFetcher(MuckrockIterFetcherBase):
    """
    Similar to the Muckrock Loop fetcher, but behaves
    as a generator instead of a loop
    """

    async def generator_fetch(self) -> str:
        """
        Fetches data and yields status messages between requests
        """
        url = self.build_url(self.initial_request)
        final_message = "No more records found. Exiting..."
        while url is not None:
            try:
                data = await self.get_response(url)
            except RequestFailureException:
                final_message = "Request unexpectedly failed. Exiting..."
                break

            yield self.process_results(data["results"])
            url = data["next"]

        yield final_message



