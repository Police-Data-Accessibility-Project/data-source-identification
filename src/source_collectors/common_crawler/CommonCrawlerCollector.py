from src.collector_manager.AsyncCollectorBase import AsyncCollectorBase
from src.collector_manager.enums import CollectorType
from src.core.preprocessors.CommonCrawlerPreprocessor import CommonCrawlerPreprocessor
from src.source_collectors.common_crawler.CommonCrawler import CommonCrawler
from src.source_collectors.common_crawler.DTOs import CommonCrawlerInputDTO


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