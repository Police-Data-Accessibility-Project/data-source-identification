"""
Base class for all collectors
"""
import abc
import threading
import time
from abc import ABC
from typing import Optional

from marshmallow import Schema, ValidationError
from pydantic import BaseModel

from collector_manager.enums import CollectorStatus, CollectorType


class CollectorCloseInfo(BaseModel):
    collector_type: CollectorType
    status: CollectorStatus
    data: dict = None
    logs: list[str]
    message: str = None
    compute_time: float

class CollectorBase(ABC):
    config_schema: Schema = None # Schema for validating configuration
    output_schema: Schema = None # Schema for validating output
    collector_type: CollectorType = None # Collector type

    def __init__(self, name: str, config: dict) -> None:
        self.name = name
        self.config = self.validate_config(config)
        self.data = {}
        self.logs = []
        self.status = CollectorStatus.RUNNING
        self.start_time = None
        self.compute_time = None
        # # TODO: Determine how to update this in some of the other collectors
        self._stop_event = threading.Event()

    @abc.abstractmethod
    def run_implementation(self) -> None:
        raise NotImplementedError

    def start_timer(self) -> None:
        self.start_time = time.time()

    def stop_timer(self) -> None:
        self.compute_time = time.time() - self.start_time

    def run(self) -> None:
        try:
            self.start_timer()
            self.run_implementation()
            self.stop_timer()
            self.status = CollectorStatus.COMPLETED
            self.log("Collector completed successfully.")
        except Exception as e:
            self.stop_timer()
            self.status = CollectorStatus.ERRORED
            self.log(f"Error: {e}")

    def log(self, message: str) -> None:
        self.logs.append(message)

    def abort(self) -> CollectorCloseInfo:
        self._stop_event.set()
        self.stop_timer()
        return CollectorCloseInfo(
            status=CollectorStatus.ABORTED,
            message="Collector aborted.",
            logs=self.logs,
            compute_time=self.compute_time,
            collector_type=self.collector_type
        )

    def close(self):
        logs = self.logs
        compute_time = self.compute_time

        try:
            data = self.validate_output(self.data)
            status = CollectorStatus.COMPLETED
            message = "Collector closed and data harvested successfully."
        except Exception as e:
            data = self.data
            status = CollectorStatus.ERRORED
            message = str(e)

        return CollectorCloseInfo(
            status=status,
            data=data,
            logs=logs,
            message=message,
            compute_time=compute_time,
            collector_type=self.collector_type
        )


    def validate_output(self, output: dict) -> dict:
        if self.output_schema is None:
            raise NotImplementedError("Subclasses must define a schema.")
        try:
            schema = self.output_schema()
            return schema.load(output)
        except ValidationError as e:
            self.status = CollectorStatus.ERRORED
            raise ValueError(f"Invalid output: {e.messages}")

    def validate_config(self, config: dict) -> dict:
        if self.config_schema is None:
            raise NotImplementedError("Subclasses must define a schema.")
        try:
            return self.config_schema().load(config)
        except ValidationError as e:
            raise ValueError(f"Invalid configuration: {e.messages}")