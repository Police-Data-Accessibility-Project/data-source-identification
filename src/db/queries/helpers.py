from sqlalchemy.dialects import postgresql

from src.db.constants import STANDARD_ROW_LIMIT


def add_page_offset(statement, page, limit=STANDARD_ROW_LIMIT):
    offset = (page - 1) * limit
    return statement.limit(limit).offset(offset)
