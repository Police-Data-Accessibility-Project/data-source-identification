from typing import final

from typing_extensions import override

from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.core.tasks.url.operators.root_url.convert import convert_to_flag_root_url_pydantic, \
    convert_to_url_root_url_mapping, convert_to_url_insert_models, convert_to_root_url_links
from src.core.tasks.url.operators.root_url.models.root_mapping import URLRootURLMapping
from src.core.tasks.url.operators.root_url.queries.get import GetURLsForRootURLTaskQueryBuilder
from src.core.tasks.url.operators.root_url.queries.lookup.query import LookupRootURLsQueryBuilder
from src.core.tasks.url.operators.root_url.queries.lookup.response import LookupRootsURLResponse
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

        await self.link_urls_to_task(
            url_ids=[mapping.url_id for mapping in all_task_mappings]
        )

        # Get the Root URLs for all URLs
        mapper = URLMapper(all_task_mappings)

        # -- Identify and Derive Root URLs --

        root_url_mappings: list[URLRootURLMapping] = convert_to_url_root_url_mapping(all_task_mappings)

        # For those where the URL is also the Root URL, separate them
        original_root_urls: list[str] = [mapping.url for mapping in root_url_mappings if mapping.is_root_url]
        derived_root_urls: list[str] = [mapping.root_url for mapping in root_url_mappings if not mapping.is_root_url]

        # -- Add new Derived Root URLs --

        # For derived Root URLs, we need to check if they are already in the database
        derived_root_url_lookup_responses: list[LookupRootsURLResponse] = await self._lookup_root_urls(derived_root_urls)

        # For those not already in the database, we need to add them and get their mappings
        derived_root_urls_not_in_db: list[str] = [
            response.url
            for response in derived_root_url_lookup_responses
            if response.url_id is None
        ]
        new_derived_root_url_mappings: list[URLMapping] = await self._add_new_urls(derived_root_urls_not_in_db)

        # Add these to the mapper
        mapper.add_mappings(new_derived_root_url_mappings)

        # -- Flag Root URLs --

        # Of those we obtain, we need to get those that are not yet flagged as Root URLs
        extant_derived_root_url_ids_not_flagged: list[int] = [
            response.url_id
            for response in derived_root_url_lookup_responses
            if response.url_id is not None and not response.flagged_as_root
        ]
        original_root_url_ids_not_flagged: list[int] = [
            mapper.get_id(url)
            for url in original_root_urls
        ]
        new_derived_root_url_ids_not_flagged: list[int] = [
            mapping.url_id
            for mapping in new_derived_root_url_mappings
        ]

        all_root_url_ids_not_flagged: list[int] = list(set(
            extant_derived_root_url_ids_not_flagged +
            new_derived_root_url_ids_not_flagged +
            original_root_url_ids_not_flagged
        ))

        await self._flag_root_urls(all_root_url_ids_not_flagged)

        # -- Add Root URL Links --

        branch_url_mappings: list[URLRootURLMapping] = [mapping for mapping in root_url_mappings if not mapping.is_root_url]
        await self._add_root_url_links(
            mapper,
            root_url_mappings=branch_url_mappings,
        )

    async def _add_root_url_links(
        self,
        mapper: URLMapper,
        root_url_mappings: list[URLRootURLMapping],
    ):
        # For all task URLs that are not root URLs (i.e. 'branch' URLs):
        # - Connect them to the Root URL
        # - Add the link

        branch_urls: list[str] = [mapping.url for mapping in root_url_mappings]
        root_urls: list[str] = [mapping.root_url for mapping in root_url_mappings]

        root_url_db_mappings: list[URLMapping] = await self._lookup_root_urls(root_urls)
        task_url_db_mappings: list[URLMapping] = mapper.get_mappings_by_url(branch_urls)

        links: list[LinkURLRootURLPydantic] = convert_to_root_url_links(
            root_db_mappings=root_url_db_mappings,
            branch_db_mappings=task_url_db_mappings,
            url_root_url_mappings=root_url_mappings
        )
        await self._add_link_url_root_urls(links)

    async def _flag_root_urls(
        self,
        url_ids: list[int]
    ):
        await self._flag_as_root_urls(url_ids)

    async def _get_urls_for_root_url_task(self) -> list[URLMapping]:
        builder = GetURLsForRootURLTaskQueryBuilder()
        return await self.adb_client.run_query_builder(builder)

    async def _lookup_root_urls(self, urls: list[str]) -> list[LookupRootsURLResponse]:
        builder = LookupRootURLsQueryBuilder(urls=list(set(urls)))
        return await self.adb_client.run_query_builder(builder)

    async def _add_new_urls(self, urls: list[str]) -> list[URLMapping]:
        if len(urls) == 0:
            return []
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
        await self.adb_client.bulk_insert(links)
