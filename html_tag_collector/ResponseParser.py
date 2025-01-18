import json
from collections import namedtuple
from dataclasses import asdict
from enum import Enum
from typing import Optional

import bs4
from bs4 import BeautifulSoup
from requests import Response

from html_tag_collector.DataClassTags import ResponseHTMLInfo
from html_tag_collector.RootURLCache import RootURLCache
from html_tag_collector.constants import HEADER_TAGS
from html_tag_collector.url_adjustment_functions import drop_hostname, remove_trailing_backslash, add_https
from html_tag_collector.util import remove_excess_whitespace

VerifiedResponse = namedtuple("VerifiedResponse", "verified http_response")

class ParserTypeEnum(Enum):
    LXML = "lxml"
    LXML_XML = "lxml-xml"

class HTMLResponseParser:
    def __init__(self, root_url_cache: RootURLCache):
        self.root_url_cache = root_url_cache

    async def parse(self, url_response: Response) -> ResponseHTMLInfo:
        html_info = ResponseHTMLInfo()
        self.add_url_and_path(html_info, url_response)
        self.add_root_page_titles(html_info)
        parser_type = self.get_parser_type(url_response)
        if parser_type is None:
            return html_info
        self.add_html_from_beautiful_soup(
            html_info=html_info,
            parser_type=parser_type,
            response=url_response
        )
        return html_info

    def add_html_from_beautiful_soup(
            self,
            html_info: ResponseHTMLInfo,
            parser_type: ParserTypeEnum,
            response: Response
    ):
        # TODO: Check type on Response and update type hinting accordingly
        soup = BeautifulSoup(
            markup=response.html.html,
            features=parser_type.value,
        )
        html_info.title = self.get_html_title(soup)
        html_info.description = self.get_meta_description(soup)
        self.add_header_tags(html_info, soup)
        html_info.div = self.get_div_text(soup)
        # Prevents most bs4 memory leaks
        if soup.html is not None:
            soup.html.decompose()

    def get_div_text(self, soup):
        div_text = ""
        MAX_WORDS = 500
        for div in soup.find_all("div"):
            text = div.get_text(" ", strip=True)
            if text is None:
                continue
            # Check if adding the current text exceeds the word limit
            if len(div_text.split()) + len(text.split()) <= MAX_WORDS:
                div_text += text + " "
            else:
                break  # Stop adding text if word limit is reached

        # Truncate to 5000 characters in case of run-on 'words'
        div_text = div_text[: MAX_WORDS * 10]

        return div_text

    def get_meta_description(self, soup: BeautifulSoup) -> str:
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag is None:
            return ""
        try:
            return remove_excess_whitespace(meta_tag["content"])
        except KeyError:
            return ""

    def add_header_tags(self, html_info: ResponseHTMLInfo, soup: BeautifulSoup):
        for header_tag in HEADER_TAGS:
            headers = soup.find_all(header_tag)
            # Retrieves and drops headers containing links to reduce training bias
            header_content = [header.get_text(" ", strip=True) for header in headers if not header.a]
            tag_content = json.dumps(header_content, ensure_ascii=False)
            if tag_content == "[]":
                continue
            setattr(html_info, header_tag, tag_content)

    def get_html_title(self, soup: BeautifulSoup) -> Optional[str]:
        if soup.title is None:
            return None
        if soup.title.string is None:
            return None
        return remove_excess_whitespace(soup.title.string)


    def add_url_and_path(self, html_info: ResponseHTMLInfo, response: Response):
        url = response.url
        url = add_https(url)
        html_info.url = url

        url_path = drop_hostname(url)
        url_path = remove_trailing_backslash(url_path)
        html_info.url_path = url_path

    def add_root_page_titles(self, html_info: ResponseHTMLInfo):
        html_info.root_page_title = remove_excess_whitespace(
            self.root_url_cache.get_title(html_info.url)
        )

    def get_parser_type(self, response: Response) -> ParserTypeEnum or None:
        try:
            content_type = response.headers["content-type"]
            # If content type does not contain "html" or "xml" then we can assume that the content is unreadable
            if "html" in content_type:
                return ParserTypeEnum.LXML
            if "xml" in content_type:
                return ParserTypeEnum.LXML_XML
            return None
        except KeyError:
            return None


class ResponseParser:

    def __init__(self, url_response, root_url_cache: RootURLCache):
        self.response = url_response["response"]
        self.root_url_cache = root_url_cache
        self.tags = ResponseHTMLInfo()

        self.tags.index = url_response["index"]

    def get_url(self):
        url = self.response.url
        url = add_https(url)
        url_path = drop_hostname(url)
        url_path = remove_trailing_backslash(url_path)
        return url, url_path

    def get_parser_type(self):
        """Retrieves the parser type to use with BeautifulSoup.

        Args:
            res (HTMLResponse|Response): Response object to read the content-type from.

        Returns:
            str|bool: A string of the parser to use, or False if not readable.
        """
        # Attempt to read the content-type, set the parser accordingly to avoid warning messages
        try:
            content_type = self.response.headers["content-type"]
        except KeyError:
            return False

        # If content type does not contain "html" or "xml" then we can assume that the content is unreadable
        if "html" in content_type:
            parser = "lxml"
        elif "xml" in content_type:
            parser = "lxml-xml"
        else:
            return False

        return parser

    def verify_response(self) -> VerifiedResponse:
        # The response is None if there was an error during connection, meaning there is no content to read
        if self.response is None:
            return VerifiedResponse(False, -1)

        # If the connection did not return a 200 code, we can assume there is no relevant content to read
        http_response = self.response.status_code
        if not self.response.ok:
            return VerifiedResponse(False, http_response)

        return VerifiedResponse(True, http_response)

    def parse(self):
        if self.response is None:
            return asdict(self.tags)
        self.tags.url, self.tags.url_path = self.get_url()
        self.tags.root_page_title = remove_excess_whitespace(
            self.root_url_cache.get_title(self.tags.url)
        )
        vr: VerifiedResponse = self.verify_response()
        if not vr.verified:
            return asdict(self.tags)

        # Soup Methods
        parser_type = self.get_parser_type()
        if parser_type is False:
            return asdict(self.tags)

        try:
            soup = BeautifulSoup(self.response.html.html, parser_type)
        except (bs4.builder.ParserRejectedMarkup, AssertionError, AttributeError):
            return asdict(self.tags)

        self.tags.title = self.get_html_title(soup)

        self.tags.description = self.get_meta_description(soup)

        self.tags = self.get_header_tags(soup)

        self.tags.div = self.get_div_text(soup)

        # Prevents most bs4 memory leaks
        if soup.html:
            soup.html.decompose()

        return asdict(self.tags)

    def get_div_text(self, soup):
        """Retrieves the div text from a BeautifulSoup object.

        Args:
            soup (BeautifulSoup): BeautifulSoup object to pull the div text from.

        Returns:
            str: The div text.
        """
        # Extract max 500 words of text from HTML <div>'s
        div_text = ""
        MAX_WORDS = 500
        for div in soup.find_all("div"):
            text = div.get_text(" ", strip=True)
            if text:
                # Check if adding the current text exceeds the word limit
                if len(div_text.split()) + len(text.split()) <= MAX_WORDS:
                    div_text += text + " "
                else:
                    break  # Stop adding text if word limit is reached

        # Truncate to 5000 characters in case of run-on 'words'
        div_text = div_text[: MAX_WORDS * 10]

        return div_text

    def get_header_tags(self, soup):
        """Updates the Tags DataClass with the header tags.

        Args:
            soup (BeautifulSoup): BeautifulSoup object to pull the header tags from.

        Returns:
            ResponseHTMLInfo: DataClass with updated header tags.
        """
        for header_tag in HEADER_TAGS:
            headers = soup.find_all(header_tag)
            # Retrieves and drops headers containing links to reduce training bias
            header_content = [header.get_text(" ", strip=True) for header in headers if not header.a]
            tag_content = json.dumps(header_content, ensure_ascii=False)
            setattr(self.tags, header_tag, tag_content)

        return self.tags

    def get_html_title(self, soup):
        """Retrieves the HTML title from a BeautifulSoup object.

        Args:
            soup (BeautifulSoup): BeautifulSoup object to pull the HTML title from.

        Returns:
            str: The HTML title.
        """
        html_title = ""

        if soup.title is not None and soup.title.string is not None:
            html_title = remove_excess_whitespace(soup.title.string)

        return html_title

    def get_meta_description(self, soup):
        """Retrieves the meta description from a BeautifulSoup object.

        Args:
            soup (BeautifulSoup): BeautifulSoup object to pull the meta description from.

        Returns:
            str: The meta description.
        """
        meta_tag = soup.find("meta", attrs={"name": "description"})
        try:
            meta_description = remove_excess_whitespace(meta_tag["content"]) if meta_tag is not None else ""
        except KeyError:
            return ""

        return meta_description