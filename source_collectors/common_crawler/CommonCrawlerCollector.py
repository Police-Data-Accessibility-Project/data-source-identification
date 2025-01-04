from collector_manager.CollectorBase import CollectorBase
from collector_manager.enums import CollectorType
from core.preprocessors.CommonCrawlerPreprocessor import CommonCrawlerPreprocessor
from source_collectors.common_crawler.CommonCrawler import CommonCrawler
from source_collectors.common_crawler.DTOs import CommonCrawlerInputDTO


class CommonCrawlerCollector(CollectorBase):
    collector_type = CollectorType.COMMON_CRAWLER
    preprocessor = CommonCrawlerPreprocessor

    def run_implementation(self) -> None:
        print("Running Common Crawler...")
        dto: CommonCrawlerInputDTO = self.dto
        common_crawler = CommonCrawler(
            crawl_id=dto.common_crawl_id,
            url=dto.url,
            keyword=dto.search_term,
            start_page=dto.start_page,
            num_pages=dto.total_pages
        )
        for status in common_crawler.run():
            self.log(status)

        self.data = {"urls": common_crawler.url_results}