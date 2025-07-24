from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from src.api.endpoints.review.approve.dto import FinalReviewApprovalInfo
from src.collectors.enums import URLStatus
from src.db.constants import PLACEHOLDER_AGENCY_NAME
from src.db.models.instantiations.agency.sqlalchemy import Agency
from src.db.models.instantiations.confirmed_url_agency import LinkURLAgency
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.instantiations.url.optional_data_source_metadata import URLOptionalDataSourceMetadata
from src.db.models.instantiations.url.reviewing_user import ReviewingUserURL
from src.db.queries.base.builder import QueryBuilderBase


class ApproveURLQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        user_id: int,
        approval_info: FinalReviewApprovalInfo
    ):
        super().__init__()
        self.user_id = user_id
        self.approval_info = approval_info

    async def run(self, session: AsyncSession) -> None:
        # Get URL
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

        query = (
            Select(URL)
            .where(URL.id == self.approval_info.url_id)
            .options(
                joinedload(URL.optional_data_source_metadata),
                joinedload(URL.confirmed_agencies),
            )
        )

        url = await session.execute(query)
        url = url.scalars().first()

        update_if_not_none(
            url,
            "record_type",
            self.approval_info.record_type.value
            if self.approval_info.record_type is not None else None,
            required=True
        )

        # Get existing agency ids
        existing_agencies = url.confirmed_agencies or []
        existing_agency_ids = [agency.agency_id for agency in existing_agencies]
        new_agency_ids = self.approval_info.agency_ids or []
        if len(existing_agency_ids) == 0 and len(new_agency_ids) == 0:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Must specify agency_id if URL does not already have a confirmed agency"
            )

        # Get any existing agency ids that are not in the new agency ids
        # If new agency ids are specified, overwrite existing
        if len(new_agency_ids) != 0:
            for existing_agency in existing_agencies:
                if existing_agency.id not in new_agency_ids:
                    # If the existing agency id is not in the new agency ids, delete it
                    await session.delete(existing_agency)
        # Add any new agency ids that are not in the existing agency ids
        for new_agency_id in new_agency_ids:
            if new_agency_id not in existing_agency_ids:
                # Check if the new agency exists in the database
                query = (
                    select(Agency)
                    .where(Agency.agency_id == new_agency_id)
                )
                existing_agency = await session.execute(query)
                existing_agency = existing_agency.scalars().first()
                if existing_agency is None:
                    # If not, create it
                    agency = Agency(
                        agency_id=new_agency_id,
                        name=PLACEHOLDER_AGENCY_NAME,
                    )
                    session.add(agency)

                # If the new agency id is not in the existing agency ids, add it
                confirmed_url_agency = LinkURLAgency(
                    url_id=self.approval_info.url_id,
                    agency_id=new_agency_id
                )
                session.add(confirmed_url_agency)

        # If it does, do nothing

        url.outcome = URLStatus.VALIDATED.value

        update_if_not_none(url, "name", self.approval_info.name, required=True)
        update_if_not_none(url, "description", self.approval_info.description, required=True)

        optional_metadata = url.optional_data_source_metadata
        if optional_metadata is None:
            url.optional_data_source_metadata = URLOptionalDataSourceMetadata(
                record_formats=self.approval_info.record_formats,
                data_portal_type=self.approval_info.data_portal_type,
                supplying_entity=self.approval_info.supplying_entity
            )
        else:
            update_if_not_none(
                optional_metadata,
                "record_formats",
                self.approval_info.record_formats
            )
            update_if_not_none(
                optional_metadata,
                "data_portal_type",
                self.approval_info.data_portal_type
            )
            update_if_not_none(
                optional_metadata,
                "supplying_entity",
                self.approval_info.supplying_entity
            )

        # Add approving user
        approving_user_url = ReviewingUserURL(
            user_id=self.user_id,
            url_id=self.approval_info.url_id
        )

        session.add(approving_user_url)