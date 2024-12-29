"""
Example collector
Exists as a proof of concept for collector functionality

"""
import time

from collector_manager.CollectorBase import CollectorBase
from collector_manager.DTOs.ExampleInputDTO import ExampleInputDTO
from collector_manager.DTOs.ExampleOutputDTO import ExampleOutputDTO
from collector_manager.enums import CollectorStatus, CollectorType


class ExampleCollector(CollectorBase):
    collector_type = CollectorType.EXAMPLE

    def run_implementation(self) -> None:
        dto: ExampleInputDTO = self.dto
        sleep_time = dto.sleep_time
        for i in range(sleep_time):  # Simulate a task
            if self._stop_event.is_set():
                self.log("Collector stopped.")
                self.status = CollectorStatus.ERRORED
                return
            self.log(f"Step {i + 1}/{sleep_time}")
            time.sleep(1)  # Simulate work
        self.data = ExampleOutputDTO(
            message=f"Data collected by {self.batch_id}",
            urls=["https://example.com", "https://example.com/2"],
            parameters=self.dto.model_dump(),
        )
