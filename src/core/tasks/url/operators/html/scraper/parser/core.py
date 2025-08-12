import json

from bs4 import BeautifulSoup

from src.core.tasks.url.operators.html.scraper.parser.constants import HEADER_TAGS
from src.core.tasks.url.operators.html.scraper.parser.dtos.response_html import ResponseHTMLInfo
from src.core.tasks.url.operators.html.scraper.parser.enums import ParserTypeEnum
from src.core.tasks.url.operators.html.scraper.parser.util import remove_excess_whitespace, add_https, \
    remove_trailing_backslash, \
    drop_hostname


class HTMLResponseParser:

    async def parse(self, url: str, html_content: str, content_type: str) -> ResponseHTMLInfo:
        html_info = ResponseHTMLInfo()
        self.add_url_and_path(html_info, html_content=html_content, url=url)
        parser_type = self.get_parser_type(content_type)
        if parser_type is None:
            return html_info
        self.add_html_from_beautiful_soup(
            html_info=html_info,
            parser_type=parser_type,
            html_content=html_content
        )
        return html_info

    def add_html_from_beautiful_soup(
            self,
            html_info: ResponseHTMLInfo,
            parser_type: ParserTypeEnum,
            html_content: str
    ) -> None:
        """
        Modifies:
            html_info
        """

        soup = BeautifulSoup(
            markup=html_content,
            features=parser_type.value,
        )
        html_info.title = self.get_html_title(soup)
        html_info.description = self.get_meta_description(soup)
        self.add_header_tags(html_info, soup)
        html_info.div = self.get_div_text(soup)
        # Prevents most bs4 memory leaks
        if soup.html is not None:
            soup.html.decompose()

    def get_div_text(self, soup: BeautifulSoup) -> str:
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

    def get_html_title(self, soup: BeautifulSoup) -> str | None:
        if soup.title is None:
            return None
        if soup.title.string is None:
            return None
        return remove_excess_whitespace(soup.title.string)


    def add_url_and_path(
        self,
        html_info: ResponseHTMLInfo,
        html_content: str,
        url: str
    ) -> None:
        """
        Modifies:
            html_info.url
            html_info.url_path
        """
        url = add_https(url)
        html_info.url = url

        url_path = drop_hostname(url)
        url_path = remove_trailing_backslash(url_path)
        html_info.url_path = url_path

    def get_parser_type(self, content_type: str) -> ParserTypeEnum | None:
        try:
            # If content type does not contain "html" or "xml" then we can assume that the content is unreadable
            if "html" in content_type:
                return ParserTypeEnum.LXML
            if "xml" in content_type:
                return ParserTypeEnum.LXML_XML
            return None
        except KeyError:
            return None

