import asyncio

from aiohttp import ClientSession
from aiohttp.web import HTTPServiceUnavailable

from src.external.huggingface.inference.constants import RELEVANCY_ENDPOINT
from src.external.huggingface.inference.models.input import BasicInput
from src.external.huggingface.inference.models.output import BasicOutput


class HuggingFaceInferenceClient:

    def __init__(
        self,
        session: ClientSession,
        token: str
    ):
        self.session = session
        self.token = token


    async def get_relevancy_annotation(
        self, input_: BasicInput, attempts: int = 3
    ) -> BasicOutput:

        for _ in range(attempts):
            try:
                async with self.session.post(
                    RELEVANCY_ENDPOINT,
                    json={
                        "inputs": input_.model_dump_json(),
                    },
                    headers={
                        "Accept": "application/json",
                        "Authorization": f"Bearer {self.token}",
                        "Content-Type": "application/json"
                    }
                ) as response:
                    response.raise_for_status()
                    result = BasicOutput(**(await response.json()))
                    break
            except HTTPServiceUnavailable as e:
                print(f"Service unavailable: {e}. Retrying after backoff...")
                await asyncio.sleep(1)
        return result
