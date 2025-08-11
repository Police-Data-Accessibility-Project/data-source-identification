from src.core.env_var_manager import EnvVarManager


def get_postgres_connection_string(is_async = False) -> str:
    return EnvVarManager.get().get_postgres_connection_string(is_async)
