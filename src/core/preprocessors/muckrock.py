from typing import List

from src.db.models.instantiations.url.core.pydantic import URLInfo
from src.core.preprocessors.base import PreprocessorBase


class MuckrockPreprocessor(PreprocessorBase):

    def preprocess(self, data: dict) -> List[URLInfo]:
        url_infos = []
        for entry in data["urls"]:
            url_info = URLInfo(
                url=entry["url"],
                collector_metadata=entry["metadata"],
            )
            url_infos.append(url_info)

        return url_infos
