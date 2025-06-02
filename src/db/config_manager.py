import os

from dotenv import load_dotenv

"""
A manager for handling various configuration statements.
"""

class ConfigManager:

    @staticmethod
    def get_sqlalchemy_echo() -> bool:
        """
        Get the value of the SQLALCHEMY_ECHO environment variable.
        SQLALCHEMY_ECHO determines whether or not to print SQL statements
        SQLALCHEMY_ECHO is set to False by default.
        """
        load_dotenv()
        echo = os.getenv("SQLALCHEMY_ECHO", False)
        return echo
