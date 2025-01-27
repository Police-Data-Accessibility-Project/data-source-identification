from typing import Optional

from pydantic import BaseModel

from collector_db.DTOs.URLWithHTML import URLWithHTML


class URLRelevanceHuggingfaceTaskInfo(BaseModel):
    url_with_html: URLWithHTML
    relevant: Optional[bool] = None
