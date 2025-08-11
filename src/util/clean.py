

def clean_url(url: str) -> str:
    # Remove Non-breaking spaces
    url = url.strip(" ")

    # Remove any fragments and everything after them
    url = url.split("#")[0]
    return url

