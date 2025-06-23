
from openai.types.chat import ParsedChatCompletion

from src.core.env_var_manager import EnvVarManager
from src.core.tasks.url.operators.record_type.llm_api.dtos.record_type_structured_output import \
    RecordTypeStructuredOutput
from src.core.tasks.url.operators.record_type.llm_api.record_classifier.base import RecordClassifierBase


class OpenAIRecordClassifier(RecordClassifierBase):

    @property
    def api_key(self):
        return EnvVarManager.get().openai_api_key

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