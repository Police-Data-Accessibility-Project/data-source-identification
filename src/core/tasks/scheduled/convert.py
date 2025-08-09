from src.core.tasks.scheduled.enums import IntervalEnum


def convert_interval_enum_to_hours(interval: IntervalEnum) -> int:
    match interval:
        case IntervalEnum.DAILY:
            return 24
        case IntervalEnum.HOURLY:
            return 1
        case _:
            raise ValueError(f"Invalid interval: {interval}")