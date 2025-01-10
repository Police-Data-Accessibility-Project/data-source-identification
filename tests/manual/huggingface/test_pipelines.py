from transformers import pipeline

def test_relevancy_pipeline():
    pipe = pipeline("text-classification", model="PDAP/url-relevance")
    urls = ["example.com", "police.com", "https://coloradosprings.gov/police-department/article/news/i-25-traffic-safety-deployment-after-stop"]
    results = pipe(urls)
    for result, url in zip(results, urls):
        print(f"{url}: {result}")
