

def clean_url(url: str) -> str:
    # Remove Non-breaking spaces
    url = url.replace("\u00A0", "")
    url = url.replace(" ", "")
    url = url.replace("%C2%A0", "")
    return url

