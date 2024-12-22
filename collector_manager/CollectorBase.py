"""
Base class for all collectors
"""
import abc
import threading
from abc import ABC
from typing import Optional

from marshmallow import Schema, ValidationError
from pydantic import BaseModel

from collector_manager.enums import Status

class CollectorCloseInfo(BaseModel):
    data: dict
    logs: list[str]
    error_msg: Optional[str] = None

class CollectorBase(ABC):
    config_schema: Schema = None # Schema for validating configuration
    output_schema: Schema = None # Schema for validating output

    def __init__(self, name: str, config: dict) -> None:
        self.name = name
        self.config = self.validate_config(config)
        self.data = {}
        self.logs = []
        self.status = Status.RUNNING
        # # TODO: Determine how to update this in some of the other collectors
        self._stop_event = threading.Event()

    @abc.abstractmethod
    def run_implementation(self) -> None:
        raise NotImplementedError

    def run(self) -> None:
        try:
            self.run_implementation()
            self.status = Status.COMPLETED
            self.log("Collector completed successfully.")
        except Exception as e:
            self.status = Status.ERRORED
            self.log(f"Error: {e}")

    def log(self, message: str) -> None:
        self.logs.append(message)

    def stop(self) -> None:
        self._stop_event.set()

    def close(self):
        try:
            data = self.validate_output(self.data)
            return CollectorCloseInfo(data=data, logs=self.logs)
        except Exception as e:
            return CollectorCloseInfo(data=self.data, logs=self.logs, error_msg=str(e))


    def validate_output(self, output: dict) -> dict:
        if self.output_schema is None:
            raise NotImplementedError("Subclasses must define a schema.")
        try:
            schema = self.output_schema()
            return schema.load(output)
        except ValidationError as e:
            self.status = Status.ERRORED
            raise ValueError(f"Invalid output: {e.messages}")

    def validate_config(self, config: dict) -> dict:
        if self.config_schema is None:
            raise NotImplementedError("Subclasses must define a schema.")
        try:
            return self.config_schema().load(config)
        except ValidationError as e:
            raise ValueError(f"Invalid configuration: {e.messages}")