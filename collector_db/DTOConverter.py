from collector_db.enums import ValidationStatus, ValidationSource, URLMetadataAttributeType
from collector_db.models import URLMetadata, ConfirmedUrlAgency, AutomatedUrlAgencySuggestion, UserUrlAgencySuggestion, \
    MetadataAnnotation
from core.DTOs.GetNextURLForAgencyAnnotationResponse import GetNextURLForAgencyAgencyInfo
from core.DTOs.GetNextURLForFinalReviewResponse import FinalReviewAnnotationRelevantInfo, \
    FinalReviewAnnotationRelevantUsersInfo, FinalReviewAnnotationRecordTypeInfo, FinalReviewAnnotationAgencyAutoInfo, \
    FinalReviewAnnotationAgencyInfo, FinalReviewAnnotationAgencyUserInfo
from core.enums import RecordType, SuggestionType


def get_url_metadata(
        url_metadatas: list[URLMetadata],
        validation_status: ValidationStatus,
        validation_source: ValidationSource,
        attribute: URLMetadataAttributeType
):
    for url_metadata in url_metadatas:
        if url_metadata.validation_status != validation_status.value:
            continue
        if url_metadata.validation_source != validation_source.value:
            continue
        if url_metadata.attribute != attribute.value:
            continue
        return url_metadata



class DTOConverter:

    """
    Converts SQLAlchemy objects to DTOs
    """

    @staticmethod
    def final_review_annotation_relevant_info(
        url_metadatas: list[URLMetadata]
    ) -> FinalReviewAnnotationRelevantInfo:
        relevant_metadata = get_url_metadata(
            url_metadatas=url_metadatas,
            validation_status=ValidationStatus.PENDING_VALIDATION,
            validation_source=ValidationSource.MACHINE_LEARNING,
            attribute=URLMetadataAttributeType.RELEVANT
        )
        auto_value = relevant_metadata.value if relevant_metadata else None
        if auto_value is not None:
            auto_value = (auto_value == "True")


        annotations: list[MetadataAnnotation] = relevant_metadata.annotations if relevant_metadata else []
        relevant_count = 0
        not_relevant_count = 0
        for annotation in annotations:
            if annotation.value == "True":
                relevant_count += 1
            else:
                not_relevant_count += 1
        return FinalReviewAnnotationRelevantInfo(
            auto=auto_value,
            users=FinalReviewAnnotationRelevantUsersInfo(
                relevant=relevant_count,
                not_relevant=not_relevant_count
            )
        )

    @staticmethod
    def final_review_annotation_record_type_info(
        url_metadata: list[URLMetadata]
    ):
        record_type_metadata = get_url_metadata(
            url_metadatas=url_metadata,
            validation_status=ValidationStatus.PENDING_VALIDATION,
            validation_source=ValidationSource.MACHINE_LEARNING,
            attribute=URLMetadataAttributeType.RECORD_TYPE
        )
        user_count = {}
        if record_type_metadata is None:
            auto_value = None
            annotations = []
        else:
            auto_value = RecordType(record_type_metadata.value)
            annotations = record_type_metadata.annotations
        for annotation in annotations:
            value = RecordType(annotation.value)
            if value not in user_count:
                user_count[value] = 0
            user_count[value] += 1
        # Sort users by count, descending
        user_count = dict(sorted(user_count.items(), key=lambda x: x[1], reverse=True))

        return FinalReviewAnnotationRecordTypeInfo(
            auto=auto_value,
            users=user_count
        )

    @staticmethod
    def final_review_annotation_agency_auto_info(
            automated_agency_suggestions: list[AutomatedUrlAgencySuggestion]
    ) -> FinalReviewAnnotationAgencyAutoInfo:

        if len(automated_agency_suggestions) == 0:
            return FinalReviewAnnotationAgencyAutoInfo(
                unknown=True,
                suggestions=[]
        )


        if len(automated_agency_suggestions) == 1:
            suggestion = automated_agency_suggestions[0]
            unknown = suggestion.is_unknown
        else:
            unknown = False

        if unknown:
            return FinalReviewAnnotationAgencyAutoInfo(
                unknown=True,
                suggestions=[
                    GetNextURLForAgencyAgencyInfo(
                        suggestion_type=SuggestionType.UNKNOWN,
                    )
                ]
            )

        return FinalReviewAnnotationAgencyAutoInfo(
            unknown=unknown,
            suggestions=[
                GetNextURLForAgencyAgencyInfo(
                    suggestion_type=SuggestionType.AUTO_SUGGESTION,
                    pdap_agency_id=suggestion.agency_id,
                    agency_name=suggestion.agency.name,
                    state=suggestion.agency.state,
                    county=suggestion.agency.county,
                    locality=suggestion.agency.locality
                ) for suggestion in automated_agency_suggestions
            ]
        )

    @staticmethod
    def user_url_agency_suggestion_to_final_review_annotation_agency_user_info(
        user_url_agency_suggestions: list[UserUrlAgencySuggestion]
    ) -> dict[int, FinalReviewAnnotationAgencyUserInfo]:
        d = {}
        for suggestion in user_url_agency_suggestions:
            agency = suggestion.agency
            agency_id = agency.agency_id
            if agency.agency_id not in d:
                d[agency_id] = FinalReviewAnnotationAgencyUserInfo(
                    suggestion_type=SuggestionType.MANUAL_SUGGESTION,
                    agency_name=agency.name,
                    pdap_agency_id=agency_id,
                    state=agency.state,
                    county=agency.county,
                    locality=agency.locality,
                    count=1
                )
            else:
                d[agency_id].count += 1

        # Return sorted
        return dict(sorted(d.items(), key=lambda x: x[1].count, reverse=True))


    @staticmethod
    def final_review_annotation_agency_info(
        automated_agency_suggestions: list[AutomatedUrlAgencySuggestion],
        confirmed_agencies: list[ConfirmedUrlAgency],
        user_agency_suggestions: list[UserUrlAgencySuggestion]
    ):
        if len(confirmed_agencies) == 1:
            confirmed_agency = confirmed_agencies[0]
            confirmed_agency_info = GetNextURLForAgencyAgencyInfo(
                suggestion_type=SuggestionType.CONFIRMED,
                pdap_agency_id=confirmed_agency.agency_id,
                agency_name=confirmed_agency.agency.name,
                state=confirmed_agency.agency.state,
                county=confirmed_agency.agency.county,
                locality=confirmed_agency.agency.locality
            )
            return FinalReviewAnnotationAgencyInfo(
                confirmed=confirmed_agency_info,
                users=None,
                auto=None
            )


        agency_auto_info = DTOConverter.final_review_annotation_agency_auto_info(
            automated_agency_suggestions
        )

        agency_user_info = DTOConverter.user_url_agency_suggestion_to_final_review_annotation_agency_user_info(
            user_agency_suggestions
        )

        return FinalReviewAnnotationAgencyInfo(
            confirmed=None,
            users=agency_user_info,
            auto=agency_auto_info
        )

