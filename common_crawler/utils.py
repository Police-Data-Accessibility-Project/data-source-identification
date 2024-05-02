"""
This module contains utility functions for the common_crawler package
"""


class URLWithParameters:
    """
    A class to handle URLs with parameters, allowing for easy addition of parameters
    """

    def __init__(self, url):
        self.url = url

    def add_parameter(self, parameter, value):
        if '?' in self.url:
            self.url += f"&{parameter}={value}"
        else:
            self.url += f"?{parameter}={value}"
        return self.url

    def __str__(self):
        return self.url
