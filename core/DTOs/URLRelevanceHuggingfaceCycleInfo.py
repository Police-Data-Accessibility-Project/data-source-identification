from typing import Optional

from pydantic import BaseModel

from collector_db.DTOs.URLInfo import URLInfo


class URLRelevanceHuggingfaceCycleInfo(BaseModel):
    url_info: URLInfo
    relevant: Optional[bool] = None
