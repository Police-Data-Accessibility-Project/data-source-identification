import datetime
import os
from typing import Optional


class TimestampChecker:
    def __init__(self):
        self.last_run_time: Optional[datetime.datetime] = self.load_last_run_time()

    def load_last_run_time(self) -> Optional[datetime.datetime]:
        # Check if file `last_run.txt` exists
        # If it does, load the last run time
        if os.path.exists("local_state/last_run.txt"):
            with open("local_state/last_run.txt", "r") as f:
                return datetime.datetime.strptime(
                    f.read(),
                    "%Y-%m-%d %H:%M:%S"
                )
        return None

    def last_run_within_24_hours(self):
        if self.last_run_time is None:
            return False
        return datetime.datetime.now() - self.last_run_time < datetime.timedelta(days=1)

    def set_last_run_time(self):
        # If directory `local_state` doesn't exist, create it
        if not os.path.exists("local_state"):
            os.makedirs("local_state")

        with open("local_state/last_run.txt", "w") as f:
            f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
