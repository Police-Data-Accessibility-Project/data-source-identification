from src.db.dtos.url_html_content_info import HTMLContentType

ENUM_TO_ATTRIBUTE_MAPPING = {
    HTMLContentType.TITLE: "title",
    HTMLContentType.DESCRIPTION: "description",
    HTMLContentType.H1: "h1",
    HTMLContentType.H2: "h2",
    HTMLContentType.H3: "h3",
    HTMLContentType.H4: "h4",
    HTMLContentType.H5: "h5",
    HTMLContentType.H6: "h6",
    HTMLContentType.DIV: "div"
}
