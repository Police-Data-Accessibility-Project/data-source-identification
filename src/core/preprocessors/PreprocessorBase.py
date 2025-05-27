import abc
from abc import ABC
from typing import List

from src.db.DTOs.URLInfo import URLInfo


class PreprocessorBase(ABC):
    """
    Base class for all preprocessors

    Every preprocessor must implement the preprocess method
    but otherwise can be developed however they want
    """

    @abc.abstractmethod
    def preprocess(self, data: dict) -> List[URLInfo]:
        """
        Convert the data output from a collector into a list of URLInfos
        """
        raise NotImplementedError
