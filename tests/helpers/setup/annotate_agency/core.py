from src.core.enums import SuggestionType
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.data_creator.models.creation_info.batch.v1 import BatchURLCreationInfo
from tests.helpers.setup.annotate_agency.model import AnnotateAgencySetupInfo


async def setup_for_annotate_agency(
        db_data_creator: DBDataCreator,
        url_count: int,
        suggestion_type: SuggestionType = SuggestionType.UNKNOWN,
        with_html_content: bool = True
):
    buci: BatchURLCreationInfo = await db_data_creator.batch_and_urls(
        url_count=url_count,
        with_html_content=with_html_content
    )
    await db_data_creator.auto_suggestions(
        url_ids=buci.url_ids,
        num_suggestions=1,
        suggestion_type=suggestion_type
    )

    return AnnotateAgencySetupInfo(batch_id=buci.batch_id, url_ids=buci.url_ids)
