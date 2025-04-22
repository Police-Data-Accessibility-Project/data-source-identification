from pathlib import Path


def get_absolute_path(relative_path: str) -> str:
    """
    Get absolute path, using the current file as the point of reference
    """
    current_dir = Path(__file__).parent
    absolute_path = (current_dir / relative_path).resolve()
    return str(absolute_path)


def is_absolute_path(path: str) -> str:
    if len(path) == 0:
        raise ValueError("Path is required")
    if path[0] != "/":
        raise ValueError("Container path must be absolute")
    return path
