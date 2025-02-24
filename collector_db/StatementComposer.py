
from sqlalchemy import Select, select, exists, Table, func, Subquery
from sqlalchemy.orm import aliased

from collector_db.enums import URLMetadataAttributeType, ValidationStatus
from collector_db.models import URL, URLHTMLContent, AutomatedUrlAgencySuggestion
from collector_manager.enums import URLStatus


class StatementComposer:
    """
    Assists in the composition of SQLAlchemy statements
    """

    @staticmethod
    def pending_urls_without_html_data() -> Select:
        return (select(URL).
                     outerjoin(URLHTMLContent).
                     where(URLHTMLContent.id == None).
                     where(URL.outcome == URLStatus.PENDING.value))

    @staticmethod
    def exclude_urls_with_select_metadata(
            statement: Select,
            attribute: URLMetadataAttributeType
    ) -> Select:
        return (statement.where(
                        ~exists(
                            select(URLMetadata.id).
                            where(
                                URLMetadata.url_id == URL.id,
                                URLMetadata.attribute == attribute.value
                            )
                        )
                    ))

    @staticmethod
    def exclude_url_annotated_by_user(
            statement: Select,
            user_id: int
    ) -> Select:
        return (statement.where(
                        ~exists(
                            select(MetadataAnnotation.id).
                            where(
                                MetadataAnnotation.metadata_id == URLMetadata.id,
                                MetadataAnnotation.user_id == user_id
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
        ConfirmedAgency = aliased(ConfirmedUrlAgency)

        statement = (statement
            .where(~exists().where(AutomatedSuggestion.url_id == URL.id))  # Exclude if automated suggestions exist
            .where(~exists().where(ConfirmedAgency.url_id == URL.id))
        )  # Exclude if confirmed agencies exist

        return statement

    @staticmethod
    async def get_all_html_content_for_url(subquery) -> Select:
        statement = (
            select(
                subquery.c.url,
                subquery.c.metadata_id,
                subquery.c.value,
                URLHTMLContent.content_type,
                URLHTMLContent.content,
            )
            .join(URLHTMLContent)
            .where(subquery.c.url_id == URLHTMLContent.url_id)
        )

        raw_result = await session.execute(statement)
        result = raw_result.all()