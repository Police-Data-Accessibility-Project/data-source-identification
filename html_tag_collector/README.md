# HTML tag collector
This script adds HTML properties to a JSON file of existing URLs (and their labels optionally)
*Properties added:* `title`, `meta`, and `header` HTML tags, `http_response`

# How to use
1. If running from the command line, pass the name of the file you want to run as an argument and make sure your file in the same directory. It should be populated with URLs and properties as in the example provided. If importing collector_main, it expects a polars dataframe as an input.
2. Optionally, create a virtual environment. This is especially useful if you don't already have `beautifulsoup4` and `requests` and `polars` installed. In your terminal:

```commandline
python -m venv collector-environment
source collector-environment/bin/activate
```

3. Now install the required python libraries:

```commandline
$pip install -r requirements.txt
```

4. Run `python3 collector.py urls.json`
Terminal output:

(pdapenv) Jons-MBP:html_tag_collector bonjarlow$ python3 collector.py urls.json

Total samples: 4
Batch size: 200
Number of Batches: 1 


Batch 1/1
Retrieving HTML tags...
100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 4/4 [00:00<00:00, 24.15it/s]
Parsing responses...
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 4/4 [00:00<00:00, 277.55it/s]
shape: (4, 12)
┌─────┬─────────────────────────┬───────┬───────────────┬───┬──────┬──────┬──────┬──────┐
│ id  ┆ url                     ┆ label ┆ http_response ┆ … ┆ h3   ┆ h4   ┆ h5   ┆ h6   │
│ --- ┆ ---                     ┆ ---   ┆ ---           ┆   ┆ ---  ┆ ---  ┆ ---  ┆ ---  │
│ i64 ┆ str                     ┆ str   ┆ i64           ┆   ┆ str  ┆ str  ┆ str  ┆ str  │
╞═════╪═════════════════════════╪═══════╪═══════════════╪═══╪══════╪══════╪══════╪══════╡
│ 1   ┆ https://pdap.io         ┆ Label ┆ 200           ┆ … ┆ []   ┆ []   ┆ []   ┆ []   │
│ 2   ┆ https://pdapio.io       ┆ Label ┆ -1            ┆ … ┆ null ┆ null ┆ null ┆ null │
│ 3   ┆ https://pdap.dev        ┆ Label ┆ 200           ┆ … ┆ []   ┆ []   ┆ []   ┆ []   │
│ 4   ┆ https://pdap.io/404test ┆ Label ┆ 200           ┆ … ┆ []   ┆ []   ┆ []   ┆ []   │
└─────┴─────────────────────────┴───────┴───────────────┴───┴──────┴──────┴──────┴──────┘

5. If running from the command line, check the directory: you should now have a `labeled-urls-headers.csv` file. Invalid URLs are removed. Otherewise the function returns a processed polars dataframe.

# Why does this exist?
We can use machine learning to predict whether a URL is relevant with some success, but labelers otherwise need to visit a URL in order to determine what is kept there. By adding these properties we can label data without navigating to the URL as often.
