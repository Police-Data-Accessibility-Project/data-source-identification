from http import HTTPStatus

from fastapi import HTTPException

from src.core.enums import AnnotationType
from src.core.error_manager.dtos.error_format import ErrorFormat
from src.core.error_manager.enums import ErrorTypes


class ErrorManager:

    @staticmethod
    async def raise_error(
            error_type: ErrorTypes,
            message: str,
            status_code: HTTPStatus = HTTPStatus.BAD_REQUEST
    ):
        raise HTTPException(
            status_code=status_code,
            detail=ErrorFormat(
                code=error_type,
                message=message
            ).model_dump(mode='json')
        )

    @staticmethod
    async def raise_annotation_exists_error(
            annotation_type: AnnotationType,
            url_id: int
    ):
        await ErrorManager.raise_error(
            error_type=ErrorTypes.ANNOTATION_EXISTS,
            message=f"Annotation of type {annotation_type.value} already exists"
                    f" for url {url_id}",
            status_code=HTTPStatus.CONFLICT
        )
