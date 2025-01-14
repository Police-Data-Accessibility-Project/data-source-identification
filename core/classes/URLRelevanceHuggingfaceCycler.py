from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.URLInfo import URLInfo
from collector_db.DTOs.URLMetadataInfo import URLMetadataInfo
from collector_db.models import URLAttributeType, ValidationStatus, ValidationSource
from core.DTOs.URLRelevanceHuggingfaceCycleInfo import URLRelevanceHuggingfaceCycleInfo
from hugging_face.HuggingFaceInterface import HuggingFaceInterface


class URLRelevanceHuggingfaceCycler:

    def __init__(
            self,
            adb_client: AsyncDatabaseClient,
            huggingface_interface: HuggingFaceInterface
    ):
        self.adb_client = adb_client
        self.huggingface_interface = huggingface_interface

    def cycle(self):
        # Get pending urls from Source Collector
        # with HTML data and without Relevancy Metadata
        cycle_infos = self.get_pending_url_info()
        # Pipe into Huggingface
        self.add_huggingface_relevancy(cycle_infos)

        # Put results into Database
        self.put_results_into_database(cycle_infos)

    def put_results_into_database(self, cycle_infos):
        url_metadatas = []
        for cycle_info in cycle_infos:
            url_metadata = URLMetadataInfo(
                url_id=cycle_info.url_info.url_id,
                attribute=URLAttributeType.RELEVANT,
                value=cycle_info.relevant,
                validation_status=ValidationStatus.PENDING_LABEL_STUDIO,
                validation_source=ValidationSource.MACHINE_LEARNING
            )
            url_metadatas.append(url_metadata)
        self.adb_client.add_url_metadatas(url_metadatas)

    def add_huggingface_relevancy(self, cycle_infos):
        urls = [cycle_info.url_info.url for cycle_info in cycle_infos]
        results = self.huggingface_interface.get_url_relevancy(urls)
        for cycle_info, result in zip(cycle_infos, results):
            cycle_info.relevant = result

    def get_pending_url_info(self):
        cycle_infos = []
        pending_urls: list[URLInfo] = self.adb_client.get_urls_with_html_data_and_no_relevancy_metadata()
        for url_info in pending_urls:
            cycle_info = URLRelevanceHuggingfaceCycleInfo(
                url_info=url_info
            )
            cycle_infos.append(cycle_info)
        return cycle_infos
