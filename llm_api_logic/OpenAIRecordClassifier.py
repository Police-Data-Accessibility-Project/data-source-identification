from typing import Any

from openai.types.chat import ParsedChatCompletion

from llm_api_logic.LLMRecordClassifierBase import RecordClassifierBase
from llm_api_logic.RecordTypeStructuredOutput import RecordTypeStructuredOutput
from util.helper_functions import get_from_env


class OpenAIRecordClassifier(RecordClassifierBase):

    @property
    def api_key(self):
        return get_from_env("OPENAI_API_KEY")

    @property
    def model_name(self):
        return "gpt-4o-mini-2024-07-18"

    @property
    def base_url(self):
        return None

    @property
    def response_format(self):
        return RecordTypeStructuredOutput

    @property
    def completions_func(self) -> callable:
        return self.client.beta.chat.completions.parse

    def post_process_response(self, response: ParsedChatCompletion) -> str:
        output: RecordTypeStructuredOutput = response.choices[0].message.parsed
        return output.record_type.value