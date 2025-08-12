from typing import final

from typing_extensions import override

from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.core.tasks.url.operators.root_url.convert import convert_to_flag_root_url_pydantic, \
    convert_to_url_root_url_mapping, convert_to_url_insert_models, convert_to_root_url_links
from src.core.tasks.url.operators.root_url.models.root_mapping import URLRootURLMapping
from src.core.tasks.url.operators.root_url.queries.get import GetURLsForRootURLTaskQueryBuilder
from src.core.tasks.url.operators.root_url.queries.lookup import LookupRootURLsQueryBuilder
from src.core.tasks.url.operators.root_url.queries.prereq import CheckPrereqsForRootURLTaskQueryBuilder
from src.db.client.async_ import AsyncDatabaseClient
from src.db.dtos.url.mapping import URLMapping
from src.db.enums import TaskType
from src.db.models.impl.flag.root_url.pydantic import FlagRootURLPydantic
from src.db.models.impl.link.urls_root_url.pydantic import LinkURLRootURLPydantic
from src.db.models.impl.url.core.pydantic.insert import URLInsertModel
from src.util.url_mapper import URLMapper


@final
class URLRootURLTaskOperator(URLTaskOperatorBase):

    def __init__(self, adb_client: AsyncDatabaseClient):
        super().__init__(adb_client)

    @override
    async def meets_task_prerequisites(self) -> bool:
        builder = CheckPrereqsForRootURLTaskQueryBuilder()
        return await self.adb_client.run_query_builder(builder)

    @property
    @override
    def task_type(self) -> TaskType:
        return TaskType.ROOT_URL

    @override
    async def inner_task_logic(self) -> None:
        all_task_mappings: list[URLMapping] = await self._get_urls_for_root_url_task()

        # Get the Root URLs for all URLs
        mapper = URLMapper(all_task_mappings)
        root_url_mappings: list[URLRootURLMapping] = convert_to_url_root_url_mapping(all_task_mappings)

        # For those where the URL is also the Root URL, separate them
        task_root_urls: list[str] = [mapping.root_url for mapping in root_url_mappings if mapping.is_root_url]

        await self._add_root_urls(
            mapper,
            task_root_urls=task_root_urls
        )

        await self._add_root_url_links(
            mapper,
            root_url_mappings=root_url_mappings,
            task_root_urls=task_root_urls
        )

    async def _add_root_url_links(
        self,
        mapper: URLMapper,
        root_url_mappings: list[URLRootURLMapping],
        task_root_urls: list[str]
    ):
        # For all task URLs that are not root URLs (i.e. 'branch' URLs):
        # - Connect them to the Root URL
        # - Add the link

        task_branch_urls: list[str] = [mapping.url for mapping in root_url_mappings if not mapping.is_root_url]
        root_url_db_mappings: list[URLMapping] = await self._lookup_root_urls(task_root_urls)
        task_url_db_mappings: list[URLMapping] = mapper.get_mappings_by_url(task_branch_urls)

        links: list[LinkURLRootURLPydantic] = convert_to_root_url_links(
            root_db_mappings=root_url_db_mappings,
            branch_db_mappings=task_url_db_mappings,
            url_root_url_mappings=root_url_mappings
        )
        await self._add_link_url_root_urls(links)

    async def _add_root_urls(
        self,
        mapper: URLMapper,
        task_root_urls: list[str]
    ):
        new_root_url_ids: list[int] = mapper.get_ids(task_root_urls)
        await self._flag_as_root_urls(new_root_url_ids)

    async def _get_urls_for_root_url_task(self) -> list[URLMapping]:
        builder = GetURLsForRootURLTaskQueryBuilder()
        return await self.adb_client.run_query_builder(builder)

    async def _lookup_root_urls(self, urls: list[str]) -> list[URLMapping]:
        builder = LookupRootURLsQueryBuilder(urls=urls)
        return await self.adb_client.run_query_builder(builder)

    async def _add_new_urls(self, urls: list[str]) -> list[URLMapping]:
        insert_models: list[URLInsertModel] = convert_to_url_insert_models(urls)
        url_ids: list[int] = await self.adb_client.bulk_insert(insert_models, return_ids=True)
        mappings: list[URLMapping] = []
        for url, url_id in zip(urls, url_ids):
            mappings.append(
                URLMapping(
                    url=url,
                    url_id=url_id
                )
            )
        return mappings

    async def _flag_as_root_urls(self, url_ids: list[int]) -> None:
        flag_root_urls: list[FlagRootURLPydantic] = convert_to_flag_root_url_pydantic(url_ids)
        await self.adb_client.bulk_insert(flag_root_urls)

    async def _add_link_url_root_urls(self, links: list[LinkURLRootURLPydantic]) -> None:
        await self.adb_client.bulk_insert([links])
