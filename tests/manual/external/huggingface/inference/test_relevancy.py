import pytest
from aiohttp import ClientSession

from src.external.huggingface.inference.client import HuggingFaceInferenceClient
from src.external.huggingface.inference.models.input import BasicInput
from tests.manual.external.huggingface.inference.constants import EXAMPLE_WEBSITE

from environs import Env


@pytest.mark.asyncio
async def test_huggingface_inference_relevancy_annotation():
    env = Env()
    env.read_env()
    token = env.str("HUGGINGFACE_INFERENCE_API_KEY")

    async with ClientSession() as session:
        # Get example HTML content
        response = await session.get(EXAMPLE_WEBSITE)
        html_content = await response.text()

        hf_client = HuggingFaceInferenceClient(
            session=session,
            token=token
        )
        hf_response = await hf_client.get_relevancy_annotation(
            input_=BasicInput(html=html_content)
        )
        print(hf_response)
