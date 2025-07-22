from sqlalchemy import Column, TIMESTAMP, func, Integer, ForeignKey


def get_created_at_column():
    return Column(TIMESTAMP, nullable=False, server_default=CURRENT_TIME_SERVER_DEFAULT)


def get_agency_id_foreign_column(
    nullable: bool = False
) -> Column:
    return Column(
        'agency_id',
        Integer(),
        ForeignKey('agencies.agency_id', ondelete='CASCADE'),
        nullable=nullable
    )

CURRENT_TIME_SERVER_DEFAULT = func.now()
