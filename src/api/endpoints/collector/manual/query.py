from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.collector.dtos.manual_batch.post import ManualBatchInputDTO
from src.api.endpoints.collector.dtos.manual_batch.response import ManualBatchResponseDTO
from src.collectors.enums import CollectorType, URLStatus
from src.core.enums import BatchStatus
from src.db.models.instantiations.batch import Batch
from src.db.models.instantiations.link.link_batch_urls import LinkBatchURL
from src.db.models.instantiations.url.core import URL
from src.db.models.instantiations.url.optional_data_source_metadata import URLOptionalDataSourceMetadata
from src.db.queries.base.builder import QueryBuilderBase


class UploadManualBatchQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        user_id: int,
        dto: ManualBatchInputDTO
    ):
        super().__init__()
        self.dto = dto
        self.user_id = user_id


    async def run(self, session: AsyncSession) -> ManualBatchResponseDTO:
        batch = Batch(
            strategy=CollectorType.MANUAL.value,
            status=BatchStatus.READY_TO_LABEL.value,
            parameters={
                "name": self.dto.name
            },
            user_id=self.user_id
        )
        session.add(batch)
        await session.flush()

        batch_id = batch.id
        url_ids = []
        duplicate_urls = []

        for entry in self.dto.entries:
            url = URL(
                url=entry.url,
                name=entry.name,
                description=entry.description,
                collector_metadata=entry.collector_metadata,
                outcome=URLStatus.PENDING.value,
                record_type=entry.record_type.value if entry.record_type is not None else None,
            )

            async with session.begin_nested():
                try:
                    session.add(url)
                    await session.flush()
                except IntegrityError:
                    duplicate_urls.append(entry.url)
                    continue
            await session.flush()
            link = LinkBatchURL(
                batch_id=batch_id,
                url_id=url.id
            )
            session.add(link)

            optional_metadata = URLOptionalDataSourceMetadata(
                url_id=url.id,
                record_formats=entry.record_formats,
                data_portal_type=entry.data_portal_type,
                supplying_entity=entry.supplying_entity,
            )
            session.add(optional_metadata)
            url_ids.append(url.id)

        return ManualBatchResponseDTO(
            batch_id=batch_id,
            urls=url_ids,
            duplicate_urls=duplicate_urls
        )