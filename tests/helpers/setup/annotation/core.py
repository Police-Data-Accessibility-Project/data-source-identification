from src.collectors.enums import URLStatus
from tests.helpers.db_data_creator import DBDataCreator
from tests.helpers.setup.annotation.model import AnnotationSetupInfo


async def setup_for_get_next_url_for_annotation(
        db_data_creator: DBDataCreator,
        url_count: int,
        outcome: URLStatus = URLStatus.PENDING
) -> AnnotationSetupInfo:
    batch_id = db_data_creator.batch()
    insert_urls_info = db_data_creator.urls(
        batch_id=batch_id,
        url_count=url_count,
        outcome=outcome
    )
    await db_data_creator.html_data(
        [
            url.url_id for url in insert_urls_info.url_mappings
        ]
    )
    return AnnotationSetupInfo(batch_id=batch_id, insert_urls_info=insert_urls_info)
