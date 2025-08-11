from src.collectors.impl.base import AsyncCollectorBase
from src.collectors.enums import CollectorType
from src.core.preprocessors.common_crawler import CommonCrawlerPreprocessor
from src.collectors.impl.common_crawler.crawler import CommonCrawler
from src.collectors.impl.common_crawler.input import CommonCrawlerInputDTO


class CommonCrawlerCollector(AsyncCollectorBase):
    collector_type = CollectorType.COMMON_CRAWLER
    preprocessor = CommonCrawlerPreprocessor

    async def run_implementation(self) -> None:
        print("Running Common Crawler...")
        dto: CommonCrawlerInputDTO = self.dto
        common_crawler = CommonCrawler(
            crawl_id=dto.common_crawl_id,
            url=dto.url,
            keyword=dto.search_term,
            start_page=dto.start_page,
            num_pages=dto.total_pages,
        )
        async for status in common_crawler.run():
            await self.log(status)

        self.data = {"urls": common_crawler.url_results}