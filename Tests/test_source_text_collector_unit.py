import pytest
from unittest.mock import MagicMock, patch
from source_text_collector.keyword_extractor import KeywordExtractor

@patch('keybert.KeyBERT.extract_keywords')
def test_extract_keywords(mock_extract_keywords):
    # Arrange
    mock_extract_keywords.return_value = [('keyword1', 0.8), ('keyword2', 0.7), ('keyword3', 0.6)]  # return some mock keywords
    keyword_extractor = KeywordExtractor()

    # Act
    keywords = keyword_extractor.extract_keywords("some text", n=3)

    # Assert
    mock_extract_keywords.assert_called_once_with("some text", keyphrase_ngram_range=(1, 3), stop_words='english', top_n=3)
    assert keywords == ['keyword1', 'keyword2', 'keyword3']