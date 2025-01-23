

URL_RELEVANCE_DATASET = "PDAP/urls-relevance"
TRAINING_URLS_DATASET = "PDAP/training-urls"
DATASET_TEXT_COLS =[
    "url_path",
    "html_title",
    "keywords",
    "meta_description",
    "root_page_title",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
] # Not included: "url", "http_response"
EMPTY_TEXT_VALUES = ['[""]', None, "[]", '""']