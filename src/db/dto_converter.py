from typing import Optional

from src.api.endpoints.annotate.agency.get.dto import GetNextURLForAgencyAgencyInfo
from src.api.endpoints.annotate.relevance.get.dto import RelevanceAnnotationResponseInfo
from src.api.endpoints.review.next.dto import FinalReviewAnnotationRelevantInfo, FinalReviewAnnotationRecordTypeInfo, \
    FinalReviewAnnotationAgencyAutoInfo, FinalReviewAnnotationAgencyInfo
from src.core.enums import RecordType, SuggestionType
from src.core.tasks.url.operators.url_html.scraper.parser.dtos.response_html import ResponseHTMLInfo
from src.core.tasks.url.operators.url_html.scraper.parser.mapping import ENUM_TO_ATTRIBUTE_MAPPING
from src.db.dtos.url.html_content import HTMLContentType, URLHTMLContentInfo
from src.db.dtos.url.with_html import URLWithHTML
from src.db.models.instantiations.confirmed_url_agency import LinkURLAgency
from src.db.models.instantiations.url.suggestion.agency.auto import AutomatedUrlAgencySuggestion
from src.db.models.instantiations.url.suggestion.record_type.auto import AutoRecordTypeSuggestion
from src.db.models.instantiations.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.models.instantiations.url.html_content import URLHTMLContent
from src.db.models.instantiations.url.core.sqlalchemy import URL
from src.db.models.instantiations.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.instantiations.url.suggestion.relevant.auto.sqlalchemy import AutoRelevantSuggestion
from src.db.models.instantiations.url.suggestion.relevant.user import UserRelevantSuggestion


class DTOConverter:

    """
    Converts SQLAlchemy objects to dtos
    """

    @staticmethod
    def final_review_annotation_relevant_info(
        user_suggestion: UserRelevantSuggestion,
        auto_suggestion: AutoRelevantSuggestion
    ) -> FinalReviewAnnotationRelevantInfo:

        auto_value = RelevanceAnnotationResponseInfo(
            is_relevant=auto_suggestion.relevant,
            confidence=auto_suggestion.confidence,
            model_name=auto_suggestion.model_name

        ) if auto_suggestion else None
        user_value = user_suggestion.suggested_status if user_suggestion else None
        return FinalReviewAnnotationRelevantInfo(
            auto=auto_value,
            user=user_value
        )

    @staticmethod
    def final_review_annotation_record_type_info(
        user_suggestion: UserRecordTypeSuggestion,
        auto_suggestion: AutoRecordTypeSuggestion
    ):

        if auto_suggestion is None:
            auto_value = None
        else:
            auto_value = RecordType(auto_suggestion.record_type)
        if user_suggestion is None:
            user_value = None
        else:
            user_value = RecordType(user_suggestion.record_type)

        return FinalReviewAnnotationRecordTypeInfo(
            auto=auto_value,
            user=user_value
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
        user_url_agency_suggestion: UserUrlAgencySuggestion
    ) -> Optional[GetNextURLForAgencyAgencyInfo]:
        suggestion = user_url_agency_suggestion
        if suggestion is None:
            return None
        if suggestion.is_new:
            return GetNextURLForAgencyAgencyInfo(
                suggestion_type=SuggestionType.NEW_AGENCY,
            )
        return GetNextURLForAgencyAgencyInfo(
            suggestion_type=SuggestionType.USER_SUGGESTION,
            pdap_agency_id=suggestion.agency_id,
            agency_name=suggestion.agency.name,
            state=suggestion.agency.state,
            county=suggestion.agency.county,
            locality=suggestion.agency.locality
        )


    @staticmethod
    def confirmed_agencies_to_final_review_annotation_agency_info(
        confirmed_agencies: list[LinkURLAgency]
    ) -> list[GetNextURLForAgencyAgencyInfo]:
        results = []
        for confirmed_agency in confirmed_agencies:
            agency = confirmed_agency.agency
            agency_info = GetNextURLForAgencyAgencyInfo(
                suggestion_type=SuggestionType.CONFIRMED,
                pdap_agency_id=agency.agency_id,
                agency_name=agency.name,
                state=agency.state,
                county=agency.county,
                locality=agency.locality
            )
            results.append(agency_info)
        return results


    @staticmethod
    def final_review_annotation_agency_info(
        automated_agency_suggestions: list[AutomatedUrlAgencySuggestion],
        confirmed_agencies: list[LinkURLAgency],
        user_agency_suggestion: UserUrlAgencySuggestion
    ):

        confirmed_agency_info = DTOConverter.confirmed_agencies_to_final_review_annotation_agency_info(
            confirmed_agencies
        )

        agency_auto_info = DTOConverter.final_review_annotation_agency_auto_info(
            automated_agency_suggestions
        )

        agency_user_info = DTOConverter.user_url_agency_suggestion_to_final_review_annotation_agency_user_info(
            user_agency_suggestion
        )

        return FinalReviewAnnotationAgencyInfo(
            confirmed=confirmed_agency_info,
            user=agency_user_info,
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


