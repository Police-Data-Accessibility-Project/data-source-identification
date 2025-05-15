from typing import Optional

from pydantic import BaseModel


class URL404ProbeTDO(BaseModel):
    url_id: int
    url: str
    is_404: Optional[bool] = None