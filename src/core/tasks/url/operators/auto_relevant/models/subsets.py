from src.core.tasks.url.operators.auto_relevant.models.tdo import URLRelevantTDO


class URLRelevantAnnotationOutcomeSubsets:
    success: list[URLRelevantTDO] = []
    error: list[URLRelevantTDO] = []
