from tqdm.asyncio import tqdm_asyncio

from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.core.tasks.url.operators.internet_archives.convert import convert_ia_url_mapping_to_ia_metadata
from src.core.tasks.url.operators.internet_archives.filter import filter_into_subsets
from src.core.tasks.url.operators.internet_archives.models.subset import IAURLMappingSubsets
from src.core.tasks.url.operators.internet_archives.queries.get import GetURLsForInternetArchivesTaskQueryBuilder
from src.core.tasks.url.operators.internet_archives.queries.prereq import \
    CheckURLInternetArchivesTaskPrerequisitesQueryBuilder
from src.db.client.async_ import AsyncDatabaseClient
from src.db.dtos.url.mapping import URLMapping
from src.db.enums import TaskType
from src.db.models.impl.flag.checked_for_ia.pydantic import FlagURLCheckedForInternetArchivesPydantic
from src.db.models.impl.url.error_info.pydantic import URLErrorPydanticInfo
from src.db.models.impl.url.ia_metadata.pydantic import URLInternetArchiveMetadataPydantic
from src.external.internet_archives.client import InternetArchivesClient
from src.external.internet_archives.models.ia_url_mapping import InternetArchivesURLMapping
from src.util.url_mapper import URLMapper


class URLInternetArchivesTaskOperator(URLTaskOperatorBase):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        ia_client: InternetArchivesClient
    ):
        super().__init__(adb_client)
        self.ia_client = ia_client

    @property
    def task_type(self) -> TaskType:
        return TaskType.INTERNET_ARCHIVES

    async def meets_task_prerequisites(self) -> bool:
        return await self.adb_client.run_query_builder(
            CheckURLInternetArchivesTaskPrerequisitesQueryBuilder()
        )

    async def inner_task_logic(self) -> None:
        url_mappings: list[URLMapping] = await self._get_url_mappings()
        mapper = URLMapper(url_mappings)

        await self.link_urls_to_task(mapper.get_all_ids())

        ia_mappings: list[InternetArchivesURLMapping] = await self._search_for_internet_archive_links(mapper.get_all_urls())
        await self._add_ia_flags_to_db(mapper, ia_mappings=ia_mappings)

        subsets: IAURLMappingSubsets = filter_into_subsets(ia_mappings)
        await self._add_errors_to_db(mapper, ia_mappings=subsets.error)
        await self._add_ia_metadata_to_db(mapper, ia_mappings=subsets.has_metadata)

    async def _add_errors_to_db(self, mapper: URLMapper, ia_mappings: list[InternetArchivesURLMapping]) -> None:
        url_error_info_list: list[URLErrorPydanticInfo] = []
        for ia_mapping in ia_mappings:
            url_id = mapper.get_id(ia_mapping.url)
            url_error_info = URLErrorPydanticInfo(
                url_id=url_id,
                error=ia_mapping.error,
                task_id=self.task_id
            )
            url_error_info_list.append(url_error_info)
        await self.adb_client.bulk_insert(url_error_info_list)

    async def _get_url_mappings(self) -> list[URLMapping]:
        return await self.adb_client.run_query_builder(
            GetURLsForInternetArchivesTaskQueryBuilder()
        )

    async def _search_for_internet_archive_links(self, urls: list[str]) -> list[InternetArchivesURLMapping]:
        return await tqdm_asyncio.gather(
            *[
                self.ia_client.search_for_url_snapshot(url)
                for url in urls
            ],
            timeout=60 * 10  # 10 minutes
        )

    async def _add_ia_metadata_to_db(
        self,
        url_mapper: URLMapper,
        ia_mappings: list[InternetArchivesURLMapping],
    ) -> None:
        insert_objects: list[URLInternetArchiveMetadataPydantic] = [
            convert_ia_url_mapping_to_ia_metadata(
                url_mapper=url_mapper,
                ia_mapping=ia_mapping
            )
            for ia_mapping in ia_mappings
        ]
        await self.adb_client.bulk_insert(insert_objects)

    async def _add_ia_flags_to_db(
        self, mapper: URLMapper, ia_mappings: list[InternetArchivesURLMapping]) -> None:
        flags: list[FlagURLCheckedForInternetArchivesPydantic] = []
        for ia_mapping in ia_mappings:
            url_id = mapper.get_id(ia_mapping.url)
            flag = FlagURLCheckedForInternetArchivesPydantic(
                url_id=url_id,
                success=not ia_mapping.has_error
            )
            flags.append(flag)
        await self.adb_client.bulk_insert(flags)