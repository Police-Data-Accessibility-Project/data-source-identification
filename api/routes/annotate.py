from fastapi import APIRouter, Depends, Path

from api.dependencies import get_async_core
from collector_db.enums import URLMetadataAttributeType
from core.AsyncCore import AsyncCore
from core.DTOs.GetNextRecordTypeAnnotationResponseInfo import GetNextRecordTypeAnnotationResponseOuterInfo
from core.DTOs.GetNextRelevanceAnnotationResponseInfo import GetNextRelevanceAnnotationResponseInfo, \
    GetNextRelevanceAnnotationResponseOuterInfo
from core.DTOs.GetNextURLForAgencyAnnotationResponse import GetNextURLForAgencyAnnotationResponse, \
    URLAgencyAnnotationPostInfo
from core.DTOs.GetNextURLForAnnotationResponse import GetNextURLForAnnotationResponse
from core.DTOs.RecordTypeAnnotationPostInfo import RecordTypeAnnotationPostInfo
from core.DTOs.RelevanceAnnotationPostInfo import RelevanceAnnotationPostInfo
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
) -> GetNextRelevanceAnnotationResponseOuterInfo:
    result = await async_core.get_next_url_for_relevance_annotation(
        user_id=access_info.user_id,
    )
    return result


@annotate_router.post("/relevance/{url_id}")
async def annotate_url_for_relevance_and_get_next_url(
        relevance_annotation_post_info: RelevanceAnnotationPostInfo,
        url_id: int = Path(description="The URL id to annotate"),
        async_core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info)
) -> GetNextRelevanceAnnotationResponseOuterInfo:
    """
    Post URL annotation and get next URL to annotate
    """
    await async_core.submit_url_relevance_annotation(
        user_id=access_info.user_id,
        url_id=url_id,
        relevant=relevance_annotation_post_info.is_relevant
    )
    return await async_core.get_next_url_for_relevance_annotation(
        user_id=access_info.user_id,
    )

@annotate_router.get("/record-type")
async def get_next_url_for_record_type_annotation(
        access_info: AccessInfo = Depends(get_access_info),
        async_core: AsyncCore = Depends(get_async_core),
) -> GetNextRecordTypeAnnotationResponseOuterInfo:
    result = await async_core.get_next_url_for_record_type_annotation(
        user_id=access_info.user_id,
    )
    return result

@annotate_router.post("/record-type/{url_id}")
async def annotate_url_for_record_type_and_get_next_url(
        record_type_annotation_post_info: RecordTypeAnnotationPostInfo,
        url_id: int = Path(description="The URL id to annotate"),
        async_core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info)
) -> GetNextRecordTypeAnnotationResponseOuterInfo:
    """
    Post URL annotation and get next URL to annotate
    """
    result = await async_core.submit_url_record_type_annotation(
        user_id=access_info.user_id,
        url_id=url_id,
        record_type=record_type_annotation_post_info.record_type,
    )
    return result

@annotate_router.get("/agency")
async def get_next_url_for_agency_annotation(
        access_info: AccessInfo = Depends(get_access_info),
        async_core: AsyncCore = Depends(get_async_core),
) -> GetNextURLForAgencyAnnotationResponse:
    result = await async_core.get_next_url_agency_for_annotation(
        user_id=access_info.user_id,
    )
    return result

@annotate_router.post("/agency/{url_id}")
async def annotate_url_for_agency_and_get_next_url(
        url_id: int,
        agency_annotation_post_info: URLAgencyAnnotationPostInfo,
        async_core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info)
) -> GetNextURLForAgencyAnnotationResponse:
    """
    Post URL annotation and get next URL to annotate
    """
    await async_core.submit_url_agency_annotation(
        user_id=access_info.user_id,
        url_id=url_id,
        agency_post_info=agency_annotation_post_info
    )
    result = await async_core.get_next_url_agency_for_annotation(
        user_id=access_info.user_id,
    )
    return result