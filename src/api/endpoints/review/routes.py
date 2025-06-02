from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_async_core
from src.api.endpoints.review.dtos.approve import FinalReviewApprovalInfo
from src.api.endpoints.review.dtos.get import GetNextURLForFinalReviewOuterResponse
from src.api.endpoints.review.dtos.reject import FinalReviewRejectionInfo
from src.core.core import AsyncCore
from src.security.manager import require_permission
from src.security.dtos.access_info import AccessInfo
from src.security.enums import Permissions

review_router = APIRouter(
    prefix="/review",
    tags=["Review"],
    responses={404: {"description": "Not found"}},
)

requires_final_review_permission = require_permission(Permissions.SOURCE_COLLECTOR_FINAL_REVIEW)

@review_router.get("/next-source")
async def get_next_source(
    core: AsyncCore = Depends(get_async_core),
    access_info: AccessInfo = Depends(requires_final_review_permission),
    batch_id: Optional[int] = Query(
        description="The batch id of the next URL to get. "
                    "If not specified, defaults to first qualifying URL",
        default=None),
) -> GetNextURLForFinalReviewOuterResponse:
    next_source = await core.get_next_source_for_review(batch_id=batch_id)
    return GetNextURLForFinalReviewOuterResponse(next_source=next_source)

@review_router.post("/approve-source")
async def approve_source(
    core: AsyncCore = Depends(get_async_core),
    access_info: AccessInfo = Depends(requires_final_review_permission),
    approval_info: FinalReviewApprovalInfo = FinalReviewApprovalInfo,
    batch_id: Optional[int] = Query(
        description="The batch id of the next URL to get. "
                    "If not specified, defaults to first qualifying URL",
        default=None),
) -> GetNextURLForFinalReviewOuterResponse:
    await core.approve_url(
        approval_info,
        access_info=access_info,
    )
    next_source = await core.get_next_source_for_review(batch_id=batch_id)
    return GetNextURLForFinalReviewOuterResponse(next_source=next_source)

@review_router.post("/reject-source")
async def reject_source(
    core: AsyncCore = Depends(get_async_core),
    access_info: AccessInfo = Depends(requires_final_review_permission),
    review_info: FinalReviewRejectionInfo = FinalReviewRejectionInfo,
    batch_id: Optional[int] = Query(
        description="The batch id of the next URL to get. "
                    "If not specified, defaults to first qualifying URL",
        default=None),
) -> GetNextURLForFinalReviewOuterResponse:
    await core.reject_url(
        url_id=review_info.url_id,
        access_info=access_info,
        rejection_reason=review_info.rejection_reason
    )
    next_source = await core.get_next_source_for_review(batch_id=batch_id)
    return GetNextURLForFinalReviewOuterResponse(next_source=next_source)