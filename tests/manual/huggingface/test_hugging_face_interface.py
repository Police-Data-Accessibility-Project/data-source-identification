from hugging_face.HuggingFaceInterface import HuggingFaceInterface


def test_get_url_relevancy():
    hfi = HuggingFaceInterface()
    result = hfi.get_url_relevancy("https://coloradosprings.gov/police-department/article/news/i-25-traffic-safety-deployment-after-stop")
    result = hfi.get_url_relevancy("https://example.com")

    result = hfi.get_url_relevancy("https://police.com")

