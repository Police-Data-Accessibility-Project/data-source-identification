import json
from abc import ABC, abstractmethod
from typing import Any

from openai import AsyncOpenAI

from src.core.tasks.url.operators.record_type.llm_api.dtos.record_type_structured_output import \
    RecordTypeStructuredOutput
from src.db.dtos.url_html_content_info import URLHTMLContentInfo
from src.core.tasks.url.operators.record_type.llm_api.constants import RECORD_CLASSIFICATION_QUERY_CONTENT
from src.core.tasks.url.operators.record_type.llm_api.helpers import dictify_html_info


class RecordClassifierBase(ABC):

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    @property
    @abstractmethod
    def api_key(self) -> str:
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        pass

    @property
    @abstractmethod
    def response_format(self) -> dict | RecordTypeStructuredOutput:
        pass

    @property
    @abstractmethod
    def completions_func(self) -> callable:
        pass

    def build_query_messages(self, content_infos: list[URLHTMLContentInfo]) -> list[dict[str, str]]:
        insert_content = dictify_html_info(content_infos)
        return [
            {
                "role": "system",
                "content": RECORD_CLASSIFICATION_QUERY_CONTENT
            },
            {
                "role": "user",
                "content": str(insert_content)
            }
        ]

    @abstractmethod
    def post_process_response(self, response: Any) -> str:
        pass

    async def classify_url(self, content_infos: list[URLHTMLContentInfo]) -> str:
        func = self.completions_func
        response = await func(
            model=self.model_name,
            messages=self.build_query_messages(content_infos),
            #stream=False,  # Note that this is set for DeepSeek, but may not be needed for it
            response_format=self.response_format
        )
        return self.post_process_response(response)

        result_str = response.choices[0].message.content

        result_dict = json.loads(result_str)
        return result_dict["record_type"]