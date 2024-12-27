from typing import List

from collector_db.DTOs.URLInfo import URLInfo
from core.preprocessors.PreprocessorBase import PreprocessorBase


class AutoGooglerPreprocessor(PreprocessorBase):

    def preprocess_entry(self, entry: dict) -> list[URLInfo]:
        query = entry["query"]
        query_results = entry["query_results"]
        url_infos = []
        for qr in query_results:
            url_infos.append(URLInfo(
                url=qr["url"],
                url_metadata={
                    "query": query,
                    "snippet": qr["snippet"],
                    "title": qr["title"]
                },
            ))

        return url_infos

    def preprocess(self, data: dict) -> List[URLInfo]:
        url_infos = []
        for entry in data["data"]:
            url_infos.extend(self.preprocess_entry(entry))

        return url_infos
