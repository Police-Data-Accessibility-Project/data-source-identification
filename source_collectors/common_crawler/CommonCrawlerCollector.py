from collector_manager.CollectorBase import CollectorBase
from collector_manager.enums import CollectorType
from source_collectors.common_crawler.CommonCrawler import CommonCrawler
from source_collectors.common_crawler.schemas import CommonCrawlerConfigSchema, CommonCrawlerOutputSchema


class CommonCrawlerCollector(CollectorBase):
    config_schema = CommonCrawlerConfigSchema
    output_schema = CommonCrawlerOutputSchema
    collector_type = CollectorType.COMMON_CRAWLER

    def run_implementation(self) -> None:
        print("Running Common Crawler...")
        common_crawler = CommonCrawler(
            crawl_id=self.config["common_crawl_id"],
            url=self.config["url"],
            keyword=self.config["keyword"],
            start_page=self.config["start_page"],
            num_pages=self.config["pages"]
        )
        for status in common_crawler.run():
            self.log(status)

        self.data = {"urls": common_crawler.url_results}