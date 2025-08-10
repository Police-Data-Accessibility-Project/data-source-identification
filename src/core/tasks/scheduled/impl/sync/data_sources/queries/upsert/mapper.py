from src.external.pdap.dtos.sync.data_sources import DataSourcesSyncResponseInnerInfo


class URLSyncInfoMapper:

    def __init__(self, sync_infos: list[DataSourcesSyncResponseInnerInfo]):
        self._dict: dict[str, DataSourcesSyncResponseInnerInfo] = {
            sync_info.url: sync_info
            for sync_info in sync_infos
        }

    def get(self, url: str) -> DataSourcesSyncResponseInnerInfo:
        return self._dict[url]