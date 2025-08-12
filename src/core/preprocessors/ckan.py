from datetime import datetime
from typing import List

from src.db.models.impl.url.core.pydantic.info import URLInfo


class CKANPreprocessor:

    def preprocess(self, data: dict) -> List[URLInfo]:
        url_infos = []
        for entry in data["results"]:
            url = entry["source_url"]
            del entry["source_url"]
            entry["source_last_updated"] = entry["source_last_updated"].strftime("%Y-%m-%d") if isinstance(entry["source_last_updated"], datetime) else entry["source_last_updated"]
            url_info = URLInfo(
                url=url,
                collector_metadata=entry,
            )
            url_infos.append(url_info)
        return url_infos