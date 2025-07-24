from typing import final

from sqlalchemy.ext.asyncio import AsyncSession
import src.db.session_helper as sh
from typing_extensions import override

from src.collectors.enums import URLStatus
from src.db.models.instantiations.url.core.pydantic.upsert import URLUpsertModel
from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.dtos.sync.data_sources import DataSourcesSyncResponseInnerInfo
from src.external.pdap.enums import DataSourcesURLStatus, ApprovalStatus

@final
class UpsertURLsFromDataSourcesQueryBuilder(QueryBuilderBase):

    def __init__(self, data_sources: list[DataSourcesSyncResponseInnerInfo]):
        super().__init__()
        self.data_sources = data_sources

    @override
    async def run(self, session: AsyncSession) -> None:
        await self.upsert_urls(session=session)
        await self.update_agency_links()
        await self.update_url_data_sources()

    async def upsert_urls(self, session: AsyncSession):
        results = []
        for data_source in self.data_sources:
            results.append(
                URLUpsertModel(
                    id=data_source.id,
                    name=data_source.name,
                    description=data_source.description,
                    outcome=_convert_to_source_collector_url_status(
                        ds_url_status=data_source.url_status,
                        ds_approval_status=data_source.approval_status
                    ),
                    record_type=data_source.record_type
                )
            )
        await sh.bulk_upsert(session=session, models=results)

    async def update_agency_links(self) -> None:
        """Overwrite existing url_agency links with new ones, if applicable."""
        for data_source in self.data_sources:

        # Get existing links
        pass
        # Get new links
        pass
        # Remove all links not in new links
        pass
        # Add new links
        pass


    async def update_url_data_sources(self) -> None:
        # Get existing url-data sources attributes
        pass

        # Get new url-data sources attributes
        pass

        # Overwrite all existing url-data sources attributes that are not in new
        pass

        # Add new url-data sources attributes
        pass

        raise NotImplementedError


def convert_data_sources_sync_response_to_url_upsert(
    data_sources: list[DataSourcesSyncResponseInnerInfo]
) -> list[URLUpsertModel]:
    results = []
    for data_source in data_sources:
        results.append(
            URLUpsertModel(
                id=data_source.id,
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
