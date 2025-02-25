from typing import Optional

from collector_db.DTOs.URLHTMLContentInfo import HTMLContentType, URLHTMLContentInfo
from collector_db.DTOs.URLWithHTML import URLWithHTML
from collector_db.enums import ValidationStatus, ValidationSource, URLMetadataAttributeType
from collector_db.models import AutomatedUrlAgencySuggestion, UserUrlAgencySuggestion, URLHTMLContent, URL, Agency, \
    AutoRecordTypeSuggestion, UserRecordTypeSuggestion, UserRelevantSuggestion, AutoRelevantSuggestion
from core.DTOs.GetNextURLForAgencyAnnotationResponse import GetNextURLForAgencyAgencyInfo
from core.DTOs.GetNextURLForFinalReviewResponse import FinalReviewAnnotationRelevantInfo, \
    FinalReviewAnnotationRelevantUsersInfo, FinalReviewAnnotationRecordTypeInfo, FinalReviewAnnotationAgencyAutoInfo, \
    FinalReviewAnnotationAgencyInfo, FinalReviewAnnotationAgencyUserInfo
from core.enums import RecordType, SuggestionType
from html_tag_collector.DataClassTags import convert_to_response_html_info, ResponseHTMLInfo, ENUM_TO_ATTRIBUTE_MAPPING

class DTOConverter:

    """
    Converts SQLAlchemy objects to DTOs
    """

    @staticmethod
    def final_review_annotation_relevant_info(
        user_suggestions: list[UserRelevantSuggestion],
        auto_suggestion: AutoRelevantSuggestion
    ) -> FinalReviewAnnotationRelevantInfo:

        auto_value = auto_suggestion.relevant if auto_suggestion else None

        relevant_count = 0
        not_relevant_count = 0
        for suggestion in user_suggestions:
            if suggestion.relevant:
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
        user_suggestions: list[UserRecordTypeSuggestion],
        auto_suggestion: AutoRecordTypeSuggestion
    ):

        user_count = {}
        if auto_suggestion is None:
            auto_value = None
        else:
            auto_value = RecordType(auto_suggestion.record_type)
        for suggestion in user_suggestions:
            value = RecordType(suggestion.record_type)
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
        confirmed_agency: Optional[Agency],
        user_agency_suggestions: list[UserUrlAgencySuggestion]
    ):
        if confirmed_agency is not None:
            confirmed_agency_info = GetNextURLForAgencyAgencyInfo(
                suggestion_type=SuggestionType.CONFIRMED,
                pdap_agency_id=confirmed_agency.agency_id,
                agency_name=confirmed_agency.name,
                state=confirmed_agency.state,
                county=confirmed_agency.county,
                locality=confirmed_agency.locality
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


    @staticmethod
    def url_list_to_url_with_html_list(url_list: list[URL]) -> list[URLWithHTML]:
        return [DTOConverter.url_to_url_with_html(url) for url in url_list]

    @staticmethod
    def url_to_url_with_html(url: URL) -> URLWithHTML:
        url_val = url.url
        url_id = url.id
        html_infos = []
        for html_info in url.html_content:
            html_infos.append(
                URLHTMLContentInfo(
                    **html_info.__dict__
                )
            )

        return URLWithHTML(
            url=url_val,
            url_id=url_id,
            html_infos=html_infos
        )

    @staticmethod
    def html_content_list_to_html_response_info(html_content_list: list[URLHTMLContent]):
        response_html_info = ResponseHTMLInfo()

        for html_content in html_content_list:
            content_type = HTMLContentType(html_content.content_type)
            content = html_content.content

            setattr(
                response_html_info,
                ENUM_TO_ATTRIBUTE_MAPPING[content_type],
                content
            )


        return response_html_info


