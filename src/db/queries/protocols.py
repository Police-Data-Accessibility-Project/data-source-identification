from typing import Protocol, Optional

from sqlalchemy import Select


class HasQuery(Protocol):

    def __init__(self):
        self.query: Select | None = None
