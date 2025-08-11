"""
Example collector
Exists as a proof of concept for collector functionality

"""
import asyncio

from src.collectors.impl.base import AsyncCollectorBase
from src.collectors.impl.example.dtos.input import ExampleInputDTO
from src.collectors.impl.example.dtos.output import ExampleOutputDTO
from src.collectors.enums import CollectorType
from src.core.preprocessors.example import ExamplePreprocessor


class ExampleCollector(AsyncCollectorBase):
    collector_type = CollectorType.EXAMPLE
    preprocessor = ExamplePreprocessor

    async def run_implementation(self) -> None:
        dto: ExampleInputDTO = self.dto
        sleep_time = dto.sleep_time
        for i in range(sleep_time):  # Simulate a task
            await self.log(f"Step {i + 1}/{sleep_time}")
            await self.sleep()
        self.data = ExampleOutputDTO(
            message=f"Data collected by {self.batch_id}",
            urls=["https://example.com", "https://example.com/2"],
            parameters=self.dto.model_dump(),
        )

    @staticmethod
    async def sleep():
        # Simulate work
        await asyncio.sleep(1)