from src.db.dtos.url.mapping import URLMapping


class URLMapper:

    def __init__(self, mappings: list[URLMapping]):
        self._url_to_id = {
            mapping.url: mapping.url_id
            for mapping in mappings
        }
        self._id_to_url = {
            mapping.url_id: mapping.url
            for mapping in mappings
        }

    def get_id(self, url: str) -> int:
        return self._url_to_id[url]

    def get_url(self, url_id: int) -> str:
        return self._id_to_url[url_id]

    def add_mapping(self, mapping: URLMapping) -> None:
        self._url_to_id[mapping.url] = mapping.url_id
        self._id_to_url[mapping.url_id] = mapping.url

    def add_mappings(self, mappings: list[URLMapping]) -> None:
        for mapping in mappings:
            self.add_mapping(mapping)