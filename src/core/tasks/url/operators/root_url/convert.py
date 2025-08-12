from src.db.models.impl.flag.root_url.pydantic import FlagRootURLPydantic


def convert_to_flag_root_url_pydantic(url_ids: list[int]) -> list[FlagRootURLPydantic]:
    return [FlagRootURLPydantic(url_id=url_id) for url_id in url_ids]
