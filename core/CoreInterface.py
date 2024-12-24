from typing import Optional

from collector_manager.CollectorManager import InvalidCollectorError
from collector_manager.enums import CollectorType
from core.SourceCollectorCore import SourceCollectorCore


class CoreInterface:
    """
    An interface for accessing internal core functions.

    All methods return a string describing the result of the operation
    """

    def __init__(self, core: SourceCollectorCore = SourceCollectorCore()):
        self.core = core
        self.cm = self.core.collector_manager

    def start_collector(
            self,
            collector_type: CollectorType,
            config: Optional[dict] = None
    ) -> str:
        cid = self.core.initiate_collector(
            collector_type=collector_type,
            config=config
        )
        return f"Started {collector_type.value} collector with CID: {cid}"

    def close_collector(self, cid: int) -> str:
        return self.core.harvest_collector(cid)

    def get_info(self, cid: int) -> str:
        return self.cm.get_info(cid)

    def get_status(self, cid: Optional[int] = None) -> str:
        if cid is None:
            return "\n".join(self.cm.get_status())
        else:
            return self.cm.get_status(cid)

    def list_collectors(self) -> str:
        return "\n".join(self.cm.list_collectors())
