def remove_excess_whitespace(s: str) -> str:
    """Removes leading, trailing, and excess adjacent whitespace.

    Args:
        s (str): String to remove whitespace from.

    Returns:
        str: Clean string with excess whitespace stripped.
    """
    return " ".join(s.split()).strip()
