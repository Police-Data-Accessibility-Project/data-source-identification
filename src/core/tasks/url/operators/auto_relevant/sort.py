from src.core.tasks.url.operators.auto_relevant.models.subsets import URLRelevantAnnotationOutcomeSubsets
from src.core.tasks.url.operators.auto_relevant.models.tdo import URLRelevantTDO


async def separate_success_and_error_subsets(
    tdos: list[URLRelevantTDO]
) -> URLRelevantAnnotationOutcomeSubsets:
    subsets = URLRelevantAnnotationOutcomeSubsets()
    for tdo in tdos:
        if tdo.error is not None:
            subsets.error.append(tdo)
        else:
            subsets.success.append(tdo)
    return subsets
