"""
Example collector
Exists as a proof of concept for collector functionality

"""
import asyncio

from collector_manager.AsyncCollectorBase import AsyncCollectorBase
from collector_manager.DTOs.ExampleInputDTO import ExampleInputDTO
from collector_manager.DTOs.ExampleOutputDTO import ExampleOutputDTO
from collector_manager.enums import CollectorType
from core.preprocessors.ExamplePreprocessor import ExamplePreprocessor


class ExampleCollector(AsyncCollectorBase):
    collector_type = CollectorType.EXAMPLE
    preprocessor = ExamplePreprocessor

    async def run_implementation(self) -> None:
        dto: ExampleInputDTO = self.dto
        sleep_time = dto.sleep_time
        for i in range(sleep_time):  # Simulate a task
            await self.log(f"Step {i + 1}/{sleep_time}")
            await asyncio.sleep(1)  # Simulate work
        self.data = ExampleOutputDTO(
            message=f"Data collected by {self.batch_id}",
            urls=["https://example.com", "https://example.com/2"],
            parameters=self.dto.model_dump(),
        )