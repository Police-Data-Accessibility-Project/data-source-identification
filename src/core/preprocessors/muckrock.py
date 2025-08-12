from typing import List

from src.core.preprocessors.base import PreprocessorBase
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.info import URLInfo


class MuckrockPreprocessor(PreprocessorBase):

    def preprocess(self, data: dict) -> List[URLInfo]:
        url_infos = []
        for entry in data["urls"]:
            url_info = URLInfo(
                url=entry["url"],
                collector_metadata=entry["metadata"],
                source=URLSource.COLLECTOR
            )
            url_infos.append(url_info)

        return url_infos
