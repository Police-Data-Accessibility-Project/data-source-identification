"""
Example collector
Exists as a proof of concept for collector functionality

"""
import time

from collector_manager.CollectorBase import CollectorBase
from collector_manager.enums import Status


class ExampleCollector(CollectorBase):

    def run(self):
        try:
            for i in range(10):  # Simulate a task
                if self._stop_event.is_set():
                    self.log("Collector stopped.")
                    self.status = Status.ERRORED
                    return
                self.log(f"Step {i+1}/10")
                time.sleep(1)  # Simulate work
            self.data = {"message": f"Data collected by {self.name}"}
            self.status = Status.COMPLETED
            self.log("Collector completed successfully.")
        except Exception as e:
            self.status = Status.ERRORED
            self.log(f"Error: {e}")
