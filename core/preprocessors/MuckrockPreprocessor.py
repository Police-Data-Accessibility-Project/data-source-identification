from typing import List

from collector_db.URLInfo import URLInfo
from core.preprocessors.PreprocessorBase import PreprocessorBase


class MuckrockPreprocessor(PreprocessorBase):

    def preprocess(self, data: dict) -> List[URLInfo]:
        url_infos = []
        for entry in data["urls"]:
            url_info = URLInfo(
                url=entry["url"],
                url_metadata=entry["metadata"],
            )
            url_infos.append(url_info)

        return url_infos
