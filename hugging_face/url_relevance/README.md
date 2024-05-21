# Hugging Face URL Relevance Model

This model is trained using website data from a list of potentially relevant URLs.

A "relevant" URL is one that related to criminal justice. A "relevant" website does not necessarily mean it is a "good" data source.

The latest version of the model can be found here: [https://huggingface.co/PDAP/url-relevance](https://huggingface.co/PDAP/url-relevance)

## How to use

The training script requires `Python 3.10` or lower to work.

1. `cd` into the root directory of the project
2. Create a virtual environment. In your terminal:
```commandline
python -m venv relevance-environment
source relevance-environment/bin/activate
```
3. Now install the required python libraries:
```commandline
$pip install -r requirements.txt
```
4. Run `python3 hugging_face/url_relevance/huggingface_relevance.py`
