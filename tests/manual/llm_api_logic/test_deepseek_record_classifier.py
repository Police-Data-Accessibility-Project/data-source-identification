import pytest

from collector_db.DTOs.URLHTMLContentInfo import URLHTMLContentInfo
from llm_api_logic.DeepSeekRecordClassifier import DeepSeekRecordClassifier


@pytest.mark.asyncio
async def test_deepseek_record_classifier():
    from collector_db.DTOs.URLHTMLContentInfo import HTMLContentType as hct

    d = {
        hct.TITLE: "test title",
        hct.DESCRIPTION: "test description",
        hct.H1: "test h1",
        hct.H2: "test h2",
        hct.H3: "test h3",
        hct.H4: "test h4",
        hct.H5: "test h5",
        hct.H6: "test h6",
        hct.DIV: "test div",
    }
    content_infos = []
    for k, v in d.items():
        content_info = URLHTMLContentInfo(content_type=k, content=v)
        content_infos.append(content_info)

    classifier = DeepSeekRecordClassifier()
    result = await classifier.classify_url(content_infos)
    print(result)