from typing import List

from src.db.dtos.url_info import URLInfo
from src.core.preprocessors.base import PreprocessorBase


class CommonCrawlerPreprocessor(PreprocessorBase):


    def preprocess(self, data: dict) -> List[URLInfo]:
        url_infos = []
        for url in data["urls"]:
            url_info = URLInfo(
                url=url,
            )
            url_infos.append(url_info)

        return url_infos