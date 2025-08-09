from sqlalchemy import Column, TIMESTAMP, func, Integer, ForeignKey, Enum as SAEnum
from enum import Enum as PyEnum

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

def enum_column(
    enum_type: type[PyEnum],
    name: str,
    nullable: bool = False
) -> Column[SAEnum]:
    return Column(
        SAEnum(
            enum_type,
            name=name,
            native_enum=True,
            values_callable=lambda enum_type: [e.value for e in enum_type]
        ),
        nullable=nullable
        )

def url_id_column() -> Column[int]:
    return Column(
        Integer(),
        ForeignKey('urls.id', ondelete='CASCADE'),
        nullable=False
    )

CURRENT_TIME_SERVER_DEFAULT = func.now()
