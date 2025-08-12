from urllib.parse import urlparse, ParseResult


def extract_root_url(url: str) -> str:
    parsed_url: ParseResult = urlparse(url)
    root_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return root_url