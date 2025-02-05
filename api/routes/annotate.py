from fastapi import APIRouter, Depends, Path

from api.dependencies import get_async_core
from collector_db.enums import URLMetadataAttributeType
from core.AsyncCore import AsyncCore
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
) -> GetNextURLForAnnotationResponse:
    result = await async_core.get_next_url_for_annotation(
        user_id=access_info.user_id,
        metadata_type=URLMetadataAttributeType.RELEVANT
    )
    return result


@annotate_router.post("/relevance/{metadata_id}")
async def annotate_url_for_relevance_and_get_next_url(
        relevance_annotation_post_info: RelevanceAnnotationPostInfo,
        metadata_id: int = Path(description="The metadata id for the associated URL metadata"),
        async_core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info)
) -> GetNextURLForAnnotationResponse:
    """
    Post URL annotation and get next URL to annotate
    """
    result = await async_core.submit_and_get_next_url_for_annotation(
        user_id=access_info.user_id,
        metadata_id=metadata_id,
        annotation=str(relevance_annotation_post_info.is_relevant),
        metadata_type = URLMetadataAttributeType.RELEVANT
    )
    return result

@annotate_router.get("/record-type")
async def get_next_url_for_record_type_annotation(
        access_info: AccessInfo = Depends(get_access_info),
        async_core: AsyncCore = Depends(get_async_core),
) -> GetNextURLForAnnotationResponse:
    result = await async_core.get_next_url_for_annotation(
        user_id=access_info.user_id,
        metadata_type=URLMetadataAttributeType.RECORD_TYPE
    )
    return result

@annotate_router.post("/record-type/{metadata_id}")
async def annotate_url_for_record_type_and_get_next_url(
        record_type_annotation_post_info: RecordTypeAnnotationPostInfo,
        metadata_id: int = Path(description="The metadata id for the associated URL metadata"),
        async_core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info)
) -> GetNextURLForAnnotationResponse:
    """
    Post URL annotation and get next URL to annotate
    """
    result = await async_core.submit_and_get_next_url_for_annotation(
        user_id=access_info.user_id,
        metadata_id=metadata_id,
        annotation=record_type_annotation_post_info.record_type.value,
        metadata_type=URLMetadataAttributeType.RECORD_TYPE
    )
    return result

async def get_next_url_for_agency_annotation(
        access_info: AccessInfo = Depends(get_access_info),
        async_core: AsyncCore = Depends(get_async_core),
) -> GetNextURLForAnnotationResponse:
    result = await async_core.get_next_url_for_annotation(
        user_id=access_info.user_id,
        metadata_type=URLMetadataAttributeType.AGENCY
    )
    return result

async def annotate_url_for_agency_and_get_next_url(
        agency_annotation_post_info: RecordTypeAnnotationPostInfo,
        metadata_id: int = Path(description="The metadata id for the associated URL metadata"),
        async_core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info)
) -> GetNextURLForAnnotationResponse:
    """
    Post URL annotation and get next URL to annotate
    """
    result = await async_core.submit_and_get_next_url_for_annotation(
        user_id=access_info.user_id,
        metadata_id=metadata_id,
        annotation=agency_annotation_post_info.agency.value,
        metadata_type=URLMetadataAttributeType.AGENCY
    )
    return result