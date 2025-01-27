from multimodal_transformers.model import DistilBertWithTabular
from transformers import AutoTokenizer


class URLClassifier:

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("PDAP/url-classifier")
        self.model = DistilBertWithTabular.from_pretrained("PDAP/url-classifier")
        self.model.eval()
