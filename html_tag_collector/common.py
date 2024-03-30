def get_user_agent():
    """Returns a proper user agent string to be used for requests.

    Some websites refuse the connection of automated requests, setting the User-Agent will circumvent that.

    Returns:
        str: User agent string.
    """    
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"