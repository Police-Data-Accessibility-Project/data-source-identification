from src.core.EnvVarManager import EnvVarManager


def get_postgres_connection_string(is_async = False):
    return EnvVarManager.get().get_postgres_connection_string(is_async)
