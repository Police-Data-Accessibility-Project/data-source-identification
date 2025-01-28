
from sqlalchemy import Select, select, exists, Table, func, Subquery

from collector_db.enums import URLMetadataAttributeType
from collector_db.models import URL, URLHTMLContent, URLMetadata
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
    def simple_count_subquery(model, attribute: str, label: str) -> Subquery:
        attr_value = getattr(model, attribute)
        return select(
            attr_value,
            func.count(attr_value).label(label)
        ).group_by(attr_value).subquery()

