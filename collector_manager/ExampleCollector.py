"""
Example collector
Exists as a proof of concept for collector functionality

"""
import time

from marshmallow import Schema, fields

from collector_manager.CollectorBase import CollectorBase
from collector_manager.enums import Status


class ExampleSchema(Schema):
    example_field = fields.Str(required=True)

class ExampleOutputSchema(Schema):
    message = fields.Str(required=True)

class ExampleCollector(CollectorBase):
    config_schema = ExampleSchema
    output_schema = ExampleOutputSchema

    def run_implementation(self) -> None:
        for i in range(10):  # Simulate a task
            if self._stop_event.is_set():
                self.log("Collector stopped.")
                self.status = Status.ERRORED
                return
            self.log(f"Step {i + 1}/10")
            time.sleep(1)  # Simulate work
        self.data = {"message": f"Data collected by {self.name}"}
