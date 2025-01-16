from typing import Optional

from pydantic import BaseModel

from collector_db.DTOs.URLInfo import URLInfo
from collector_db.DTOs.URLWithHTML import URLWithHTML


class URLRelevanceHuggingfaceCycleInfo(BaseModel):
    url_with_html: URLWithHTML
    relevant: Optional[bool] = None
