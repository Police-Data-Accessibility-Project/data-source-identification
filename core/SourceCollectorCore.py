from typing import Optional

from collector_db.DTOs.BatchInfo import BatchInfo
from collector_db.DatabaseClient import DatabaseClient
from collector_manager.CollectorManager import CollectorManager, InvalidCollectorError
from collector_manager.collector_mapping import COLLECTOR_MAPPING
from collector_manager.enums import CollectorType, CollectorStatus
from core.DTOs.CollectionLifecycleInfo import CollectionLifecycleInfo
from core.enums import BatchStatus
from core.preprocessors.PreprocessorBase import PreprocessorBase
from core.preprocessors.preprocessor_mapping import PREPROCESSOR_MAPPING



def collector_to_batch_status(status: CollectorStatus):
    match status:
        case CollectorStatus.COMPLETED:
            batch_status = BatchStatus.COMPLETE
        case CollectorStatus.ABORTED:
            batch_status = BatchStatus.ABORTED
        case CollectorStatus.ERRORED:
            batch_status = BatchStatus.ERROR
        case _:
            raise NotImplementedError(f"Unknown collector status: {status}")
    return batch_status


class InvalidPreprocessorError(Exception):
    pass


class SourceCollectorCore:
    def __init__(self, db_client: DatabaseClient = DatabaseClient()):
        self.db_client = db_client
        self.collector_manager = CollectorManager()
        pass


    def initiate_collector(
            self,
            collector_type: CollectorType,
            config: Optional[dict] = None,):
        """
        Reserves a batch ID from the database
        and starts the requisite collector
        """
        name = collector_type.value
        try:
            collector = COLLECTOR_MAPPING[collector_type](name, config)
        except KeyError:
            raise InvalidCollectorError(f"Collector {name} not found.")

        batch_info = BatchInfo(
            strategy=collector_type.value,
            status=BatchStatus.IN_PROCESS,
            parameters=config
        )

        batch_id = self.db_client.insert_batch(batch_info)
        self.collector_manager.start_collector(collector=collector, cid=batch_id)

        return batch_id

    def harvest_collector(self, batch_id: int) -> CollectionLifecycleInfo:
        close_info = self.collector_manager.close_collector(batch_id)
        batch_status = collector_to_batch_status(close_info.status)
        preprocessor = self.get_preprocessor(close_info.collector_type)
        url_infos = preprocessor.preprocess(close_info.data)
        self.db_client.update_batch_post_collection(
            batch_id=batch_id,
            url_count=len(url_infos),
            batch_status=batch_status,
            compute_time=close_info.compute_time
        )
        insert_url_infos = self.db_client.insert_urls(
            url_infos=url_infos,
            batch_id=batch_id
        )
        return CollectionLifecycleInfo(
            batch_id=batch_id,
            url_id_mapping=insert_url_infos.url_mappings,
            duplicates=insert_url_infos.duplicates,
            message=close_info.message
        )


    def get_preprocessor(
        self,
        collector_type: CollectorType
    ) -> PreprocessorBase:
        try:
            return PREPROCESSOR_MAPPING[collector_type]()
        except KeyError:
            raise InvalidPreprocessorError(f"Preprocessor for {collector_type} not found.")




"""
TODO: Add logic for batch processing

"""