

def clean_url(url: str) -> str:
    # Remove Non-breaking spaces
    url = url.replace("\u00A0", "")
    url = url.replace(" ", "")
    url = url.replace("%C2%A0", "")

    # Remove any fragments and everything after them
    url = url.split("#")[0]
    return url

