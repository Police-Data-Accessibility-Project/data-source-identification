from typing import List

from src.collectors.source_collectors.example.dtos.output import ExampleOutputDTO
from src.core.preprocessors.base import PreprocessorBase
from src.db.models.instantiations.url.core.pydantic.info import URLInfo


class ExamplePreprocessor(PreprocessorBase):

    def preprocess(self, data: ExampleOutputDTO) -> List[URLInfo]:
        url_infos = []
        for url in data.urls:
            url_info = URLInfo(
                url=url,
            )
            url_infos.append(url_info)

        return url_infos
