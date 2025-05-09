from typing import Any, Optional

from sqlalchemy import Select, select, exists, Table, func, Subquery, and_, not_, ColumnElement, case, literal, CTE
from sqlalchemy.orm import aliased

from collector_db.enums import URLMetadataAttributeType, ValidationStatus, TaskType
from collector_db.models import URL, URLHTMLContent, AutomatedUrlAgencySuggestion, URLOptionalDataSourceMetadata, Batch, \
    ConfirmedURLAgency, LinkTaskURL, Task, UserUrlAgencySuggestion, UserRecordTypeSuggestion, UserRelevantSuggestion, \
    AutoRecordTypeSuggestion, AutoRelevantSuggestion, ReviewingUserURL
from collector_manager.enums import URLStatus, CollectorType
from core.enums import BatchStatus


class StatementComposer:
    """
    Assists in the composition of SQLAlchemy statements
    """

    @staticmethod
    def pending_urls_without_html_data() -> Select:
        exclude_subquery = (select(1).
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
            ~exists().where(ConfirmedURLAgency.url_id == URL.id)
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
                Batch
            )

        return query


    @staticmethod
    def user_suggestion_not_exists(
            model_to_exclude: UserUrlAgencySuggestion or
                              UserRecordTypeSuggestion or
                              UserRelevantSuggestion
    ) -> ColumnElement[bool]:
        #

        subquery = not_(
                    exists(
                        select(model_to_exclude)
                        .where(
                            model_to_exclude.url_id == URL.id,
                        )
                    )
                )

        return subquery

    @staticmethod
    def count_distinct(field, label):
        return func.count(func.distinct(field)).label(label)

    @staticmethod
    def sum_distinct(field, label):
        return func.sum(func.distinct(field)).label(label)

    @staticmethod
    def url_annotation_flags_query(
            status: Optional[URLStatus] = None
    ) -> CTE:
        stmt = (
            select(
                URL.id.label("url_id"),
                case((AutoRecordTypeSuggestion.url_id != None, literal(True)), else_=literal(False)).label(
                    "has_auto_record_type_annotation"
                    ),
                case((AutoRelevantSuggestion.url_id != None, literal(True)), else_=literal(False)).label(
                    "has_auto_relevant_annotation"
                    ),
                case((AutomatedUrlAgencySuggestion.url_id != None, literal(True)), else_=literal(False)).label(
                    "has_auto_agency_annotation"
                    ),
                case((UserRecordTypeSuggestion.url_id != None, literal(True)), else_=literal(False)).label(
                    "has_user_record_type_annotation"
                    ),
                case((UserRelevantSuggestion.url_id != None, literal(True)), else_=literal(False)).label(
                    "has_user_relevant_annotation"
                    ),
                case((UserUrlAgencySuggestion.url_id != None, literal(True)), else_=literal(False)).label(
                    "has_user_agency_annotation"
                    ),
                case((ReviewingUserURL.url_id != None, literal(True)), else_=literal(False)).label("was_reviewed"),
            )
            .outerjoin(AutoRecordTypeSuggestion, URL.id == AutoRecordTypeSuggestion.url_id)
            .outerjoin(AutoRelevantSuggestion, URL.id == AutoRelevantSuggestion.url_id)
            .outerjoin(AutomatedUrlAgencySuggestion, URL.id == AutomatedUrlAgencySuggestion.url_id)
            .outerjoin(UserRecordTypeSuggestion, URL.id == UserRecordTypeSuggestion.url_id)
            .outerjoin(UserRelevantSuggestion, URL.id == UserRelevantSuggestion.url_id)
            .outerjoin(UserUrlAgencySuggestion, URL.id == UserUrlAgencySuggestion.url_id)
            .outerjoin(ReviewingUserURL, URL.id == ReviewingUserURL.url_id)
        )
        if status is not None:
            stmt = stmt.where(
                URL.outcome == status.value
            )

        return stmt.cte("url_annotation_flags")