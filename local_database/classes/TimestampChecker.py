import os
from datetime import datetime, timedelta


class TimestampChecker:
    def __init__(self):
        self.last_run_time: datetime | None = self.load_last_run_time()

    def load_last_run_time(self) -> datetime | None:
        # Check if file `last_run.txt` exists
        # If it does, load the last run time
        if os.path.exists("local_state/last_run.txt"):
            with open("local_state/last_run.txt", "r") as f:
                return datetime.strptime(
                    f.read(),
                    "%Y-%m-%d %H:%M:%S"
                )
        return None

    def last_run_within_24_hours(self) -> bool:
        if self.last_run_time is None:
            return False
        return datetime.now() - self.last_run_time < timedelta(days=1)

    def set_last_run_time(self):
        # If directory `local_state` doesn't exist, create it
        if not os.path.exists("local_state"):
            os.makedirs("local_state")

        with open("local_state/last_run.txt", "w") as f:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
