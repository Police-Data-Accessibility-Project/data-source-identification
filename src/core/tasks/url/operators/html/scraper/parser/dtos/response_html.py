from pydantic import BaseModel


class ResponseHTMLInfo(BaseModel):
    index: int = -1
    url: str = ""
    url_path: str = ""
    title: str = ""
    description: str = ""
    http_response: int = -1
    h1: str = ""
    h2: str = ""
    h3: str = ""
    h4: str = ""
    h5: str = ""
    h6: str = ""
    div: str = ""


