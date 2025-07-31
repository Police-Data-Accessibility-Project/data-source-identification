from typing import final

from typing_extensions import override

from src.api.endpoints.review.approve.dto import FinalReviewApprovalInfo
from src.api.endpoints.review.enums import RejectionReason
from src.core.enums import SuggestionType
from tests.helpers.batch_creation_parameters.annotation_info import AnnotationInfo
from tests.helpers.data_creator.commands.base import DBDataCreatorCommandBase
from tests.helpers.data_creator.commands.impl.suggestion.auto.agency import AgencyAutoSuggestionsCommand
from tests.helpers.data_creator.commands.impl.suggestion.auto.record_type import AutoRecordTypeSuggestionCommand
from tests.helpers.data_creator.commands.impl.suggestion.auto.relevant import AutoRelevantSuggestionCommand
from tests.helpers.data_creator.commands.impl.suggestion.user.agency import AgencyUserSuggestionsCommand
from tests.helpers.data_creator.commands.impl.suggestion.user.record_type import UserRecordTypeSuggestionCommand
from tests.helpers.data_creator.commands.impl.suggestion.user.relevant import UserRelevantSuggestionCommand


@final
class AnnotateCommand(DBDataCreatorCommandBase):

    def __init__(
        self,
        url_id: int,
        annotation_info: AnnotationInfo
    ):
        super().__init__()
        self.url_id = url_id
        self.annotation_info = annotation_info

    @override
    async def run(self) -> None:
        info = self.annotation_info
        if info.user_relevant is not None:
            await self.run_command(
                UserRelevantSuggestionCommand(
                    url_id=self.url_id,
                    suggested_status=info.user_relevant
                )
            )
        if info.auto_relevant is not None:
            await self.run_command(
                AutoRelevantSuggestionCommand(
                    url_id=self.url_id,
                    relevant=info.auto_relevant
                )
            )
        if info.user_record_type is not None:
            await self.run_command(
                UserRecordTypeSuggestionCommand(
                    url_id=self.url_id,
                    record_type=info.user_record_type,
                )
            )
        if info.auto_record_type is not None:
            await self.run_command(
                AutoRecordTypeSuggestionCommand(
                    url_id=self.url_id,
                    record_type=info.auto_record_type
                )
            )
        if info.user_agency is not None:
            await self.run_command(
                AgencyUserSuggestionsCommand(
                    url_id=self.url_id,
                    agency_annotation_info=info.user_agency
                )
            )
        if info.auto_agency is not None:
            await self.run_command(
                AgencyAutoSuggestionsCommand(
                    url_id=self.url_id,
                    count=1,
                    suggestion_type=SuggestionType.AUTO_SUGGESTION
                )
            )
        if info.confirmed_agency is not None:
            await self.run_command(
                AgencyAutoSuggestionsCommand(
                    url_id=self.url_id,
                    count=1,
                    suggestion_type=SuggestionType.CONFIRMED
                )
            )
        if info.final_review_approved is not None:
            if info.final_review_approved:
                final_review_approval_info = FinalReviewApprovalInfo(
                    url_id=self.url_id,
                    record_type=self.annotation_info.user_record_type,
                    agency_ids=[self.annotation_info.user_agency.suggested_agency]
                    if self.annotation_info.user_agency is not None else None,
                    description="Test Description",
                )
                await self.adb_client.approve_url(
                    approval_info=final_review_approval_info,
                    user_id=1
                )
            else:
                await self.adb_client.reject_url(
                    url_id=self.url_id,
                    user_id=1,
                    rejection_reason=RejectionReason.NOT_RELEVANT
                )
