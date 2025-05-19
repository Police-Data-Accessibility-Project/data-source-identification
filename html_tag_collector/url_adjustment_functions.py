from urllib.parse import urlparse




def add_https(url: str) -> str:
    if not url.startswith("http"):
        url = "https://" + url
    return url


def remove_trailing_backslash(url_path):
    if url_path and url_path[-1] == "/":
        url_path = url_path[:-1]
    return url_path


def drop_hostname(new_url):
    url_path = urlparse(new_url).path[1:]
    return url_path
