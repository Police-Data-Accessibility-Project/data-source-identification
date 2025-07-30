from sqlalchemy import Integer, Column, DateTime, Date

from src.db.models.templates import Base


class DataSourcesSyncState(Base):
    __tablename__ = 'data_sources_sync_state'
    id = Column(Integer, primary_key=True)
    last_full_sync_at = Column(
        DateTime(),
        nullable=True,
        comment="The datetime of the last *full* sync "
                "(i.e., the last sync that got all entries "
                "available to be synchronized)."
    )
    current_cutoff_date = Column(
        Date(),
        nullable=True,
        comment="Tracks the cutoff date passed to the data sources sync endpoint."
                "On completion of a full sync, this is set to "
                "the day before the present day."
    )
    current_page = Column(
        Integer(),
        nullable=True,
        comment="Tracks the current page passed to the data sources sync endpoint."
                "On completion of a full sync, this is set to `null`."
    )