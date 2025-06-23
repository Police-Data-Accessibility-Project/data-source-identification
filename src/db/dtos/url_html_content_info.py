from enum import Enum
from typing import Optional

from pydantic import BaseModel


class HTMLContentType(Enum):
    TITLE = "Title"
    DESCRIPTION = "Description"
    H1 = "H1"
    H2 = "H2"
    H3 = "H3"
    H4 = "H4"
    H5 = "H5"
    H6 = "H6"
    DIV = "Div"

class URLHTMLContentInfo(BaseModel):
    url_id: Optional[int] = None
    content_type: HTMLContentType
    content: str | list[str]