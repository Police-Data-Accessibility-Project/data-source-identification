from fastapi import APIRouter, Depends, Path

from api.dependencies import get_async_core
from core.AsyncCore import AsyncCore
from core.DTOs.GetNextURLForRelevanceAnnotationResponse import GetNextURLForRelevanceAnnotationResponse
from core.DTOs.RelevanceAnnotationInfo import RelevanceAnnotationPostInfo
from security_manager.SecurityManager import get_access_info, AccessInfo

annotate_router = APIRouter(
    prefix="/annotate",
    tags=["annotate"],
    responses={404: {"description": "Not found"}},
)


@annotate_router.get("/relevance")
async def get_next_url_for_relevance_annotation(
        access_info: AccessInfo = Depends(get_access_info),
        async_core: AsyncCore = Depends(get_async_core),
) -> GetNextURLForRelevanceAnnotationResponse:
    result = await async_core.get_next_url_for_relevance_annotation(user_id=access_info.user_id)
    return result


@annotate_router.post("/relevance/{metadata_id}")
async def annotate_url_for_relevance_and_get_next_url(
        relevance_annotation_post_info: RelevanceAnnotationPostInfo,
        metadata_id: int = Path(description="The metadata id for the associated URL metadata"),
        async_core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info)
) -> GetNextURLForRelevanceAnnotationResponse:
    """
    Post URL annotation and get next URL to annotate
    """
    await async_core.submit_url_relevance_annotation(
        user_id=access_info.user_id,
        metadata_id=metadata_id,
        annotation=relevance_annotation_post_info
    )
    result = await async_core.get_next_url_for_relevance_annotation(user_id=access_info.user_id)
    return result
