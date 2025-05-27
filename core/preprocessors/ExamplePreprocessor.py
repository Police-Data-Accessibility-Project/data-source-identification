from typing import List

from db.DTOs.URLInfo import URLInfo
from collector_manager.DTOs.ExampleOutputDTO import ExampleOutputDTO
from core.preprocessors.PreprocessorBase import PreprocessorBase


class ExamplePreprocessor(PreprocessorBase):

    def preprocess(self, data: ExampleOutputDTO) -> List[URLInfo]:
        url_infos = []
        for url in data.urls:
            url_info = URLInfo(
                url=url,
            )
            url_infos.append(url_info)

        return url_infos
