from abc import abstractmethod
from time import sleep

from source_collectors.muckrock.classes.exceptions.RequestFailureException import RequestFailureException
from source_collectors.muckrock.classes.muckrock_fetchers.MuckrockIterFetcherBase import MuckrockIterFetcherBase


class MuckrockLoopFetcher(MuckrockIterFetcherBase):

    async def loop_fetch(self):
        url = self.build_url(self.initial_request)
        while url is not None:
            try:
                data = await self.get_response(url)
            except RequestFailureException:
                break

            url = self.process_data(data)
            sleep(1)

    def process_data(self, data: dict):
        """
        Process data and get next url, if any
        """
        self.process_results(data["results"])
        self.report_progress()
        url = data["next"]
        return url

    @abstractmethod
    def report_progress(self):
        pass
