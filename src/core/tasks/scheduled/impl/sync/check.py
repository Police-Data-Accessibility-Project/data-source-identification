from src.core.tasks.scheduled.impl.sync.constants import MAX_SYNC_REQUESTS
from src.core.tasks.scheduled.impl.sync.exceptions import MaxRequestsExceededError


def check_max_sync_requests_not_exceeded(request_count: int) -> None:
    """
    Raises:
        MaxRequestsExceededError: If the number of requests made exceeds the maximum allowed.
    """

    if request_count > MAX_SYNC_REQUESTS:
        raise MaxRequestsExceededError(
            f"Max requests in a single task run ({MAX_SYNC_REQUESTS}) exceeded."
        )