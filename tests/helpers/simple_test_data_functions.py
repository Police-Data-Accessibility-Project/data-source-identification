"""
This page contains functions for creating simple
(i.e., primitive data type) test data
"""
import uuid


def generate_test_urls(count: int) -> list[str]:
    results = []
    for i in range(count):
        url = f"https://example.com/{uuid.uuid4().hex}"
        results.append(url)

    return results

def generate_test_html() -> str:
    return """
    <!DOCTYPE html>
    <html>
      <head>
        <title>Example HTML</title>
      </head>
      <body>
        <h1>Example HTML</h1>
        <p>This is an example of HTML content.</p>
      </body>
    </html>
    """