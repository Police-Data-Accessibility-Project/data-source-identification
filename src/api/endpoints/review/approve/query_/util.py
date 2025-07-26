from typing import Any

from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST


def update_if_not_none(
    model,
    field,
    value: Any,
    required: bool = False
):
    if value is not None:
        setattr(model, field, value)
        return
    if not required:
        return
    model_value = getattr(model, field, None)
    if model_value is None:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Must specify {field} if it does not already exist"
        )
