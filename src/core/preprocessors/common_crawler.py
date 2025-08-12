from typing import List

from src.core.preprocessors.base import PreprocessorBase
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.info import URLInfo


class CommonCrawlerPreprocessor(PreprocessorBase):


    def preprocess(self, data: dict) -> List[URLInfo]:
        url_infos = []
        for url in data["urls"]:
            url_info = URLInfo(
                url=url,
                source=URLSource.COLLECTOR
            )
            url_infos.append(url_info)

        return url_infos