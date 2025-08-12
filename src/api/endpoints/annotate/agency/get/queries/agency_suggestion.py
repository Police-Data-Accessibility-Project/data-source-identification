from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.agency.get.dto import GetNextURLForAgencyAgencyInfo
from src.core.enums import SuggestionType
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.url.suggestion.agency.auto import AutomatedUrlAgencySuggestion
from src.db.queries.base.builder import QueryBuilderBase


class GetAgencySuggestionsQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        url_id: int
    ):
        super().__init__()
        self.url_id = url_id

    async def run(self, session: AsyncSession) -> list[GetNextURLForAgencyAgencyInfo]:
        # Get relevant autosuggestions and agency info, if an associated agency exists

        statement = (
            select(
                AutomatedUrlAgencySuggestion.agency_id,
                AutomatedUrlAgencySuggestion.is_unknown,
                Agency.name,
                Agency.state,
                Agency.county,
                Agency.locality
            )
            .join(Agency, isouter=True)
            .where(AutomatedUrlAgencySuggestion.url_id == self.url_id)
        )
        raw_autosuggestions = await session.execute(statement)
        autosuggestions = raw_autosuggestions.all()
        agency_suggestions = []
        for autosuggestion in autosuggestions:
            agency_id = autosuggestion[0]
            is_unknown = autosuggestion[1]
            name = autosuggestion[2]
            state = autosuggestion[3]
            county = autosuggestion[4]
            locality = autosuggestion[5]
            agency_suggestions.append(
                GetNextURLForAgencyAgencyInfo(
                    suggestion_type=SuggestionType.AUTO_SUGGESTION if not is_unknown else SuggestionType.UNKNOWN,
                    pdap_agency_id=agency_id,
                    agency_name=name,
                    state=state,
                    county=county,
                    locality=locality
                )
            )
        return agency_suggestions