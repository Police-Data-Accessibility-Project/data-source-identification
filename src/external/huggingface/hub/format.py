from datasets import Dataset

from src.core.tasks.scheduled.impl.huggingface.queries.get.model import GetForLoadingToHuggingFaceOutput


def format_as_huggingface_dataset(outputs: list[GetForLoadingToHuggingFaceOutput]) -> Dataset:
    d = {
        'url_id': [],
        'url': [],
        'relevant': [],
        'record_type_fine': [],
        'record_type_coarse': [],
        'html': []
    }
    for output in outputs:
        d['url_id'].append(output.url_id)
        d['url'].append(output.url)
        d['relevant'].append(output.relevant)
        d['record_type_fine'].append(output.record_type_fine.value)
        d['record_type_coarse'].append(output.record_type_coarse.value)
        d['html'].append(output.html)
    return Dataset.from_dict(d)

