from typing import Any

from sqlalchemy import Select, select, exists, Table, func, Subquery, and_
from sqlalchemy.orm import aliased

from collector_db.enums import URLMetadataAttributeType, ValidationStatus
from collector_db.models import URL, URLHTMLContent, AutomatedUrlAgencySuggestion, URLOptionalDataSourceMetadata, Batch, \
    ConfirmedURLAgency
from collector_manager.enums import URLStatus, CollectorType


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