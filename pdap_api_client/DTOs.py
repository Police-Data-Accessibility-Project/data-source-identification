from pydantic import BaseModel


class MatchAgencyInfo(BaseModel):
    submitted_name: str
    id: str