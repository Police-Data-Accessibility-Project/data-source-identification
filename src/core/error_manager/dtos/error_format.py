from pydantic import BaseModel

from src.core.error_manager.enums import ErrorTypes


class ErrorFormat(BaseModel):
    code: ErrorTypes
    message: str
