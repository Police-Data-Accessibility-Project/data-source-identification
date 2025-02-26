from fastapi import APIRouter, Depends

from api.dependencies import get_async_core
from core.AsyncCore import AsyncCore
from core.DTOs.FinalReviewApprovalInfo import FinalReviewApprovalInfo
from core.DTOs.GetNextURLForFinalReviewResponse import GetNextURLForFinalReviewResponse, \
    GetNextURLForFinalReviewOuterResponse
from security_manager.SecurityManager import AccessInfo, get_access_info

review_router = APIRouter(
    prefix="/review",
    tags=["Review"],
    responses={404: {"description": "Not found"}},
)

@review_router.get("/next-source")
async def get_next_source(
    core: AsyncCore = Depends(get_async_core),
    access_info: AccessInfo = Depends(get_access_info),
) -> GetNextURLForFinalReviewOuterResponse:
    next_source = await core.get_next_source_for_review()
    return GetNextURLForFinalReviewOuterResponse(next_source=next_source)

@review_router.post("/approve-source")
async def approve_source(
    core: AsyncCore = Depends(get_async_core),
    access_info: AccessInfo = Depends(get_access_info),
    approval_info: FinalReviewApprovalInfo = FinalReviewApprovalInfo
) -> GetNextURLForFinalReviewOuterResponse:
    next_source = await core.approve_and_get_next_source_for_review(approval_info)
    return GetNextURLForFinalReviewOuterResponse(next_source=next_source)