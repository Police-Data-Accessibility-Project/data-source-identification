# HTML tag collector
This script adds HTML properties to a JSON file of existing URLs.
*Properties added:* `title`, `meta`, and `header` HTML tags, `http_response`

# How to use
1. Make sure you have a `urls.json` file in the same directory. It should be populated with URLs and properties as in the example provided.
2. Optionally, create a virtual environment. This is especially useful if you don't already have `beautifulsoup4` and `requests` installed. In your terminal:
```
python -m venv collector-environment
source collector-environment/bin/activate
```
3. Run `pip install beautifulsoup4` and `pip install requests`, if they are not installed already.
4. Run `python3 collector.py`.
5. Check the directory: you should now have a `urls_and_tags.json` file. Invalid URLs are removed.

# Why does this exist?
We can use machine learning to predict whether a URL is relevant with some success, but labelers otherwise need to visit a URL in order to determine what is kept there. By adding these properties we can label data without navigating to the URL as often.
