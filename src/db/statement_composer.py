from typing import Any

from sqlalchemy import Select, select, exists, func, Subquery, and_, not_, ColumnElement
from sqlalchemy.orm import aliased, selectinload

from src.collectors.enums import URLStatus
from src.core.enums import BatchStatus
from src.db.constants import STANDARD_ROW_LIMIT
from src.db.enums import TaskType
from src.db.models.instantiations.confirmed_url_agency import LinkURLAgency
from src.db.models.instantiations.link.link_batch_urls import LinkBatchURL
from src.db.models.instantiations.link.link_task_url import LinkTaskURL
from src.db.models.instantiations.task.core import Task
from src.db.models.instantiations.url.html_content import URLHTMLContent
from src.db.models.instantiations.url.optional_data_source_metadata import URLOptionalDataSourceMetadata
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.instantiations.batch.sqlalchemy import Batch
from src.db.models.instantiations.url.suggestion.agency.auto import AutomatedUrlAgencySuggestion
from src.db.types import UserSuggestionType


class StatementComposer:
    """
    Assists in the composition of SQLAlchemy statements
    """

    @staticmethod
    def pending_urls_without_html_data() -> Select:
        exclude_subquery = (
            select(1).
            select_from(LinkTaskURL).
            join(Task, LinkTaskURL.task_id == Task.id).
            where(LinkTaskURL.url_id == URL.id).
            where(Task.task_type == TaskType.HTML.value).
            where(Task.task_status == BatchStatus.READY_TO_LABEL.value)
         )
        query = (
            select(URL).
            outerjoin(URLHTMLContent).
            where(URLHTMLContent.id == None).
            where(~exists(exclude_subquery)).
            where(URL.outcome == URLStatus.PENDING.value)
            .options(
                selectinload(URL.batch)
            )
        )
        return query

    @staticmethod
    def exclude_urls_with_extant_model(
        statement: Select,
        model: Any
    ):
        return (statement.where(
                        ~exists(
                            select(model.id).
                            where(
                                model.url_id == URL.id
                            )
                        )
                    ))

    @staticmethod
    def simple_count_subquery(model, attribute: str, label: str) -> Subquery:
        attr_value = getattr(model, attribute)
        return select(
            attr_value,
            func.count(attr_value).label(label)
        ).group_by(attr_value).subquery()

    @staticmethod
    def exclude_urls_with_agency_suggestions(
            statement: Select
    ):
        # Aliases for clarity
        AutomatedSuggestion = aliased(AutomatedUrlAgencySuggestion)

        # Exclude if automated suggestions exist
        statement = statement.where(
            ~exists().where(AutomatedSuggestion.url_id == URL.id)
        )
        # Exclude if confirmed agencies exist
        statement = statement.where(
            ~exists().where(LinkURLAgency.url_id == URL.id)
        )
        return statement

    @staticmethod
    def pending_urls_missing_miscellaneous_metadata_query() -> Select:
        query = select(URL).where(
            and_(
                    URL.outcome == URLStatus.PENDING.value,
                    URL.name == None,
                    URL.description == None,
                    URLOptionalDataSourceMetadata.url_id == None
                )
            ).outerjoin(
                URLOptionalDataSourceMetadata
            ).join(
                LinkBatchURL
            ).join(
                Batch
            )

        return query

    @staticmethod
    def user_suggestion_exists(
        model_to_include: UserSuggestionType
    ) -> ColumnElement[bool]:
        subquery = exists(
            select(model_to_include)
            .where(
                model_to_include.url_id == URL.id,
            )
        )
        return subquery

    @staticmethod
    def user_suggestion_not_exists(
            model_to_exclude: UserSuggestionType
    ) -> ColumnElement[bool]:
        subquery = not_(
            StatementComposer.user_suggestion_exists(model_to_exclude)
        )
        return subquery

    @staticmethod
    def count_distinct(field, label):
        return func.count(func.distinct(field)).label(label)

    @staticmethod
    def sum_distinct(field, label):
        return func.sum(func.distinct(field)).label(label)

    @staticmethod
    def add_limit_and_page_offset(query: Select, page: int):
        zero_offset_page = page - 1
        rows_offset = zero_offset_page * STANDARD_ROW_LIMIT
        return query.offset(
            rows_offset
        ).limit(
            STANDARD_ROW_LIMIT
        )
