
"""
Some websites refuse the connection of automated requests,
setting the User-Agent will circumvent that.
"""
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"

REQUEST_HEADERS = {
        "User-Agent": USER_AGENT,
        # Make sure there's no pre-mature closing of responses before a redirect completes
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    }
HEADER_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6"]
