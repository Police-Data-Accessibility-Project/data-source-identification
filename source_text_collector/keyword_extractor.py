import asyncio

import requests
import yake
from bs4 import BeautifulSoup
from keybert import KeyBERT


# from multi_rake import Rake

class KeywordExtractor:
    """
    This class is used to extract keywords from text using the KeyBERT algorithm.
    """

    def __init__(self):
        self.model = KeyBERT(model='all-mpnet-base-v2')

    def extract_keywords(self, text: str, n=10) -> list[str]:
        """
        Extract keywords from text using KeyBERT algorithm.
        Args:
            text: The text to extract keywords from.
            n: The number of keywords to extract.

        Returns: The top n keywords extracted from the text.
        """
        keywords = self.model.extract_keywords(text, keyphrase_ngram_range=(1, 3), stop_words='english', top_n=n)
        return [keyword for keyword, _ in keywords]
