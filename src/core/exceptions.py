from http import HTTPStatus

from fastapi import HTTPException


class MuckrockAPIError(Exception):
    pass


class MatchAgencyError(Exception):
    pass


class FailedValidationException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=HTTPStatus.BAD_REQUEST, detail=detail)
