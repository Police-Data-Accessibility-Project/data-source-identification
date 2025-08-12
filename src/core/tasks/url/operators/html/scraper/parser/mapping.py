from src.db.models.impl.url.html.content.enums import HTMLContentType

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
