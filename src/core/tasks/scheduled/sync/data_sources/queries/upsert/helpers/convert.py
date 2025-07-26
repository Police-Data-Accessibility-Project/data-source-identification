from src.collectors.enums import URLStatus
from src.core.tasks.scheduled.sync.data_sources.queries.upsert.url.insert.params import \
    InsertURLForDataSourcesSyncParams
from src.core.tasks.scheduled.sync.data_sources.queries.upsert.url.update.params import \
    UpdateURLForDataSourcesSyncParams
from src.external.pdap.dtos.sync.data_sources import DataSourcesSyncResponseInnerInfo
from src.external.pdap.enums import DataSourcesURLStatus, ApprovalStatus


def convert_to_source_collector_url_status(
    ds_url_status: DataSourcesURLStatus,
    ds_approval_status: ApprovalStatus
) -> URLStatus:
    match ds_url_status:
        case DataSourcesURLStatus.AVAILABLE:
            raise NotImplementedError("Logic not implemented for this status.")
        case DataSourcesURLStatus.NONE_FOUND:
            raise NotImplementedError("Logic not implemented for this status.")
        case DataSourcesURLStatus.BROKEN:
            return URLStatus.NOT_FOUND
        case _:
            pass

    match ds_approval_status:
        case ApprovalStatus.APPROVED:
            return URLStatus.VALIDATED
        case ApprovalStatus.REJECTED:
            return URLStatus.NOT_RELEVANT
        case ApprovalStatus.NEEDS_IDENTIFICATION:
            return URLStatus.PENDING
        case ApprovalStatus.PENDING:
            return URLStatus.PENDING
        case _:
            raise NotImplementedError(f"Logic not implemented for this approval status: {ds_approval_status}")

def convert_to_url_update_params(
    url_id: int,
    sync_info: DataSourcesSyncResponseInnerInfo
) -> UpdateURLForDataSourcesSyncParams:
    return UpdateURLForDataSourcesSyncParams(
        id=url_id,
        name=sync_info.name,
        description=sync_info.description,
        outcome=convert_to_source_collector_url_status(
            ds_url_status=sync_info.url_status,
            ds_approval_status=sync_info.approval_status
        ),
        record_type=sync_info.record_type
    )

def convert_to_url_insert_params(
    url: str,
    sync_info: DataSourcesSyncResponseInnerInfo
) -> InsertURLForDataSourcesSyncParams:
    return InsertURLForDataSourcesSyncParams(
        url=url,
        name=sync_info.name,
        description=sync_info.description,
        outcome=convert_to_source_collector_url_status(
            ds_url_status=sync_info.url_status,
            ds_approval_status=sync_info.approval_status
        ),
        record_type=sync_info.record_type
    )
