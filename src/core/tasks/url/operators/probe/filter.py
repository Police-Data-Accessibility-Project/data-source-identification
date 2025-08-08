from src.core.tasks.url.operators.probe.tdo import URLProbeTDO


def filter_non_redirect_tdos(tdos: list[URLProbeTDO]) -> list[URLProbeTDO]:
    return [tdo for tdo in tdos if not tdo.response.is_redirect]

def filter_redirect_tdos(tdos: list[URLProbeTDO]) -> list[URLProbeTDO]:
    return [tdo for tdo in tdos if tdo.response.is_redirect]