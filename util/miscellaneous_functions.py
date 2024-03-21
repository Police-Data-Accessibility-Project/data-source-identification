from datetime import datetime


def get_filename_friendly_timestamp() -> str:
    # Get the current datetime
    now = datetime.now()
    # Format the datetime in a filename-friendly format
    # Example: "2024-03-20_15-30-45"
    return now.strftime("%Y-%m-%d_%H-%M-%S")
