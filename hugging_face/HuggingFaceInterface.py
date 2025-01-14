from transformers import pipeline

class HuggingFaceInterface:

    def __init__(self):
        self.pipe = pipeline("text-classification", model="PDAP/url-relevance")

    def get_url_relevancy(self, urls: list[str], threshold: float = 0.8) -> list[bool]:
        results: list[list[dict]] = self.pipe(urls)
        for result, url in zip(results, urls):
            result.append({"url": url})

        bool_results = []
        for result in results:
            score = result[0]["score"]
            if score >= threshold:
                bool_results.append(True)
            else:
                bool_results.append(False)
        return bool_results




