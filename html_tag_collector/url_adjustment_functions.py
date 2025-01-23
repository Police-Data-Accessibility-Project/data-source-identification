from urllib.parse import urlparse


def standardize_url_prefixes(urls: list[tuple[str]]):
    new_urls = []
    for url_tup in urls:
        url = url_tup[0]
        # TODO: Need logic for if URL is none -- should not be included
        # (also an unlikely case in the Source Collector)
        url = add_https(url)
        new_urls.append(url)
    return new_urls


def http_to_https(url):
    # Assumes url is in http format
    if not url[4] == "s":
        url = url[:4] + "s" + url[4:]
    return url


async def remove_json_suffix(url):
    if url is not None:
        url = url.removesuffix(".json")
    return url


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
