from src.collectors.enums import CollectorType
from src.collectors.impl.muckrock.api_interface.core import MuckrockAPIInterface
from src.core.tasks.url.operators.agency_identification.subtasks.impl.base import AgencyIdentificationSubtaskBase
from src.core.tasks.url.operators.agency_identification.subtasks.impl.ckan import CKANAgencyIdentificationSubtask
from src.core.tasks.url.operators.agency_identification.subtasks.impl.muckrock import \
    MuckrockAgencyIdentificationSubtask
from src.core.tasks.url.operators.agency_identification.subtasks.impl.unknown import UnknownAgencyIdentificationSubtask
from src.external.pdap.client import PDAPClient


class AgencyIdentificationSubtaskLoader:
    """Loads subtasks and associated dependencies."""

    def __init__(
        self,
        pdap_client: PDAPClient,
        muckrock_api_interface: MuckrockAPIInterface
    ):
        self.pdap_client = pdap_client
        self.muckrock_api_interface = muckrock_api_interface

    async def _load_muckrock_subtask(self) -> MuckrockAgencyIdentificationSubtask:
        return MuckrockAgencyIdentificationSubtask(
            muckrock_api_interface=self.muckrock_api_interface,
            pdap_client=self.pdap_client
        )

    async def _load_ckan_subtask(self) -> CKANAgencyIdentificationSubtask:
        return CKANAgencyIdentificationSubtask(
            pdap_client=self.pdap_client
        )

    async def load_subtask(self, collector_type: CollectorType) -> AgencyIdentificationSubtaskBase:
        """Get subtask based on collector type."""
        match collector_type:
            case CollectorType.MUCKROCK_SIMPLE_SEARCH:
                return await self._load_muckrock_subtask()
            case CollectorType.MUCKROCK_COUNTY_SEARCH:
                return await self._load_muckrock_subtask()
            case CollectorType.MUCKROCK_ALL_SEARCH:
                return await self._load_muckrock_subtask()
            case CollectorType.AUTO_GOOGLER:
                return UnknownAgencyIdentificationSubtask()
            case CollectorType.COMMON_CRAWLER:
                return UnknownAgencyIdentificationSubtask()
            case CollectorType.CKAN:
                return await self._load_ckan_subtask()
        return UnknownAgencyIdentificationSubtask()