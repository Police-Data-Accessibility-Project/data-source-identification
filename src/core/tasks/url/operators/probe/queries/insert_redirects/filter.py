from src.db.dtos.url.mapping import URLMapping


def filter_new_dest_urls(
    url_mappings_in_db: list[URLMapping],
    all_dest_urls: list[str]
) -> list[str]:
    extant_destination_urls: set[str] = set([url_mapping.url for url_mapping in url_mappings_in_db])
    new_dest_urls: list[str] = [
        url
        for url in all_dest_urls
        if url not in extant_destination_urls
    ]
    return new_dest_urls