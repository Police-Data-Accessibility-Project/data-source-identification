from src.api.endpoints.review.dtos.base import FinalReviewBaseInfo
from src.api.endpoints.review.enums import RejectionReason


class FinalReviewRejectionInfo(FinalReviewBaseInfo):
    rejection_reason: RejectionReason = RejectionReason.NOT_RELEVANT
