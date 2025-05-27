"""
Manager for all collectors
Can start, stop, and get info on running collectors
And manages the retrieval of collector info
"""

class InvalidCollectorError(Exception):
    pass
