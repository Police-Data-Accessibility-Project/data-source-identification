from typing import List

from src.core.preprocessors.base import PreprocessorBase
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.info import URLInfo


class AutoGooglerPreprocessor(PreprocessorBase):

    def preprocess_entry(self, entry: dict) -> list[URLInfo]:
        query = entry["query"]
        query_results = entry["query_results"]
        url_infos = []
        for qr in query_results:
            url_infos.append(URLInfo(
                url=qr["url"],
                collector_metadata={
                    "query": query,
                    "snippet": qr["snippet"],
                    "title": qr["title"]
                },
                source=URLSource.COLLECTOR
            ))

        return url_infos

    def preprocess(self, data: dict) -> List[URLInfo]:
        url_infos = []
        for entry in data["data"]:
            url_infos.extend(self.preprocess_entry(entry))

        return url_infos
