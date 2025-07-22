from src.collectors.enums import URLStatus
from src.db.models.instantiations.url.core.pydantic.upsert import URLUpsertModel
from src.external.pdap.dtos.sync.data_sources import DataSourcesSyncResponseInnerInfo
from src.external.pdap.enums import DataSourcesURLStatus, ApprovalStatus



def convert_data_sources_sync_response_to_url_upsert(
    data_sources: list[DataSourcesSyncResponseInnerInfo]
) -> list[URLUpsertModel]:
    results = []
    for data_source in data_sources:
        results.append(
            URLUpsertModel(
                id=data_source.id,
                url=data_source.url,
                name=data_source.name,
                description=data_source.description,
                outcome=_convert_to_source_collector_url_status(
                    ds_url_status=data_source.url_status,
                    ds_approval_status=data_source.approval_status
                ),
                record_type=data_source.record_type
            )
        )
    return results


def _convert_to_source_collector_url_status(
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
