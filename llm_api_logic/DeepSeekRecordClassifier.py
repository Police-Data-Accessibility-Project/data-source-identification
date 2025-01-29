import json
import os

from openai import AsyncOpenAI

from collector_db.DTOs.URLHTMLContentInfo import URLHTMLContentInfo
from core.enums import RecordType
from llm_api_logic.LLMRecordClassifierBase import RecordClassifierBase

class DeepSeekRecordClassifier(RecordClassifierBase):


    @property
    def api_key(self):
        return os.getenv("DEEPSEEK_API_KEY")

    @property
    def model_name(self):
        return "deepseek-chat"

    @property
    def base_url(self):
        return "https://api.deepseek.com"

    @property
    def response_format(self):
        return {
            'type': 'json_object'
        }

    @property
    def completions_func(self) -> callable:
        return AsyncOpenAI.chat.completions.create