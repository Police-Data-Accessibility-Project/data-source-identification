"""
Tracks the status of the agencies sync
"""

from sqlalchemy import DateTime, Date, Integer, Column

from src.db.models.templates import Base


class AgenciesSyncState(Base):
    __tablename__ = 'agencies_sync_state'

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
        comment="Tracks the cutoff date passed to the agencies sync endpoint."
                "On completion of a full sync, this is set to "
                "the day before the present day."
    )
    current_page = Column(
        Integer(),
        nullable=True,
        comment="Tracks the current page passed to the agencies sync endpoint."
                "On completion of a full sync, this is set to `null`."
    )