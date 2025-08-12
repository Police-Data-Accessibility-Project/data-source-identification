from typing import Optional

from pydantic import BaseModel


class URLAgencyAnnotationPostInfo(BaseModel):
    is_new: bool = False
    suggested_agency: int | None = None
