from typing import Optional

from fastapi import APIRouter, Depends, Path, Query

from src.api.dependencies import get_async_core
from src.api.endpoints.annotate.dtos.agency.post import URLAgencyAnnotationPostInfo
from src.api.endpoints.annotate.dtos.agency.response import GetNextURLForAgencyAnnotationResponse
from src.api.endpoints.annotate.dtos.all.post import AllAnnotationPostInfo
from src.api.endpoints.annotate.dtos.all.response import GetNextURLForAllAnnotationResponse
from src.api.endpoints.annotate.dtos.record_type.post import RecordTypeAnnotationPostInfo
from src.api.endpoints.annotate.dtos.record_type.response import GetNextRecordTypeAnnotationResponseOuterInfo
from src.api.endpoints.annotate.dtos.relevance.post import RelevanceAnnotationPostInfo
from src.api.endpoints.annotate.dtos.relevance.response import GetNextRelevanceAnnotationResponseOuterInfo
from src.core.core import AsyncCore
from src.security.manager import get_access_info
from src.security.dtos.access_info import AccessInfo

annotate_router = APIRouter(
    prefix="/annotate",
    tags=["annotate"],
    responses={404: {"description": "Not found"}},
)

batch_query = Query(
    description="The batch id of the next URL to get. "
                "If not specified, defaults to first qualifying URL",
    default=None
)

@annotate_router.get("/relevance")
async def get_next_url_for_relevance_annotation(
        access_info: AccessInfo = Depends(get_access_info),
        async_core: AsyncCore = Depends(get_async_core),
        batch_id: Optional[int] = Query(
            description="The batch id of the next URL to get. "
                        "If not specified, defaults to first qualifying URL",
            default=None),
) -> GetNextRelevanceAnnotationResponseOuterInfo:
    return await async_core.get_next_url_for_relevance_annotation(
        user_id=access_info.user_id,
        batch_id=batch_id
    )


@annotate_router.post("/relevance/{url_id}")
async def annotate_url_for_relevance_and_get_next_url(
        relevance_annotation_post_info: RelevanceAnnotationPostInfo,
        url_id: int = Path(description="The URL id to annotate"),
        async_core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info),
        batch_id: Optional[int] = batch_query
) -> GetNextRelevanceAnnotationResponseOuterInfo:
    """
    Post URL annotation and get next URL to annotate
    """
    await async_core.submit_url_relevance_annotation(
        user_id=access_info.user_id,
        url_id=url_id,
        suggested_status=relevance_annotation_post_info.suggested_status
    )
    return await async_core.get_next_url_for_relevance_annotation(
        user_id=access_info.user_id,
        batch_id=batch_id
    )

@annotate_router.get("/record-type")
async def get_next_url_for_record_type_annotation(
        access_info: AccessInfo = Depends(get_access_info),
        async_core: AsyncCore = Depends(get_async_core),
        batch_id: Optional[int] = batch_query
) -> GetNextRecordTypeAnnotationResponseOuterInfo:
    return await async_core.get_next_url_for_record_type_annotation(
        user_id=access_info.user_id,
        batch_id=batch_id
    )

@annotate_router.post("/record-type/{url_id}")
async def annotate_url_for_record_type_and_get_next_url(
        record_type_annotation_post_info: RecordTypeAnnotationPostInfo,
        url_id: int = Path(description="The URL id to annotate"),
        async_core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info),
        batch_id: Optional[int] = batch_query
) -> GetNextRecordTypeAnnotationResponseOuterInfo:
    """
    Post URL annotation and get next URL to annotate
    """
    await async_core.submit_url_record_type_annotation(
        user_id=access_info.user_id,
        url_id=url_id,
        record_type=record_type_annotation_post_info.record_type,
    )
    return await async_core.get_next_url_for_record_type_annotation(
        user_id=access_info.user_id,
        batch_id=batch_id
    )

@annotate_router.get("/agency")
async def get_next_url_for_agency_annotation(
        access_info: AccessInfo = Depends(get_access_info),
        async_core: AsyncCore = Depends(get_async_core),
        batch_id: Optional[int] = batch_query
) -> GetNextURLForAgencyAnnotationResponse:
    return await async_core.get_next_url_agency_for_annotation(
        user_id=access_info.user_id,
        batch_id=batch_id
    )

@annotate_router.post("/agency/{url_id}")
async def annotate_url_for_agency_and_get_next_url(
        url_id: int,
        agency_annotation_post_info: URLAgencyAnnotationPostInfo,
        async_core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info),
        batch_id: Optional[int] = batch_query
) -> GetNextURLForAgencyAnnotationResponse:
    """
    Post URL annotation and get next URL to annotate
    """
    await async_core.submit_url_agency_annotation(
        user_id=access_info.user_id,
        url_id=url_id,
        agency_post_info=agency_annotation_post_info
    )
    return await async_core.get_next_url_agency_for_annotation(
        user_id=access_info.user_id,
        batch_id=batch_id
    )

@annotate_router.get("/all")
async def get_next_url_for_all_annotations(
        access_info: AccessInfo = Depends(get_access_info),
        async_core: AsyncCore = Depends(get_async_core),
        batch_id: Optional[int] = batch_query
) -> GetNextURLForAllAnnotationResponse:
    return await async_core.get_next_url_for_all_annotations(
        batch_id=batch_id
    )

@annotate_router.post("/all/{url_id}")
async def annotate_url_for_all_annotations_and_get_next_url(
        url_id: int,
        all_annotation_post_info: AllAnnotationPostInfo,
        async_core: AsyncCore = Depends(get_async_core),
        access_info: AccessInfo = Depends(get_access_info),
        batch_id: Optional[int] = batch_query
) -> GetNextURLForAllAnnotationResponse:
    """
    Post URL annotation and get next URL to annotate
    """
    await async_core.submit_url_for_all_annotations(
        user_id=access_info.user_id,
        url_id=url_id,
        post_info=all_annotation_post_info
    )
    return await async_core.get_next_url_for_all_annotations(
        batch_id=batch_id
    )