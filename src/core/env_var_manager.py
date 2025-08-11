import os

class EnvVarManager:
    _instance = None
    _allow_direct_init = False  # internal flag

    """
    A class for unified management of environment variables
    """
    def __new__(cls, *args, **kwargs):
        if not cls._allow_direct_init:
            raise RuntimeError("Use `EnvVarManager.get()` or `EnvVarManager.override()` instead.")
        return super().__new__(cls)

    def __init__(self, env: dict = os.environ):
        self.env = env
        self._load()

    def _load(self) -> None:
        """Load environment variables from environment"""

        self.google_api_key = self.require_env("GOOGLE_API_KEY")
        self.google_cse_id = self.require_env("GOOGLE_CSE_ID")

        self.pdap_email = self.require_env("PDAP_EMAIL")
        self.pdap_password = self.require_env("PDAP_PASSWORD")
        self.pdap_api_key = self.require_env("PDAP_API_KEY")
        self.pdap_api_url = self.require_env("PDAP_API_URL")

        self.discord_webhook_url = self.require_env("DISCORD_WEBHOOK_URL")

        self.openai_api_key = self.require_env("OPENAI_API_KEY")
        self.hf_inference_api_key = self.require_env("HUGGINGFACE_INFERENCE_API_KEY")
        self.hf_hub_token = self.require_env("HUGGINGFACE_HUB_TOKEN")

        self.postgres_user = self.require_env("POSTGRES_USER")
        self.postgres_password = self.require_env("POSTGRES_PASSWORD")
        self.postgres_host = self.require_env("POSTGRES_HOST")
        self.postgres_port = self.require_env("POSTGRES_PORT")
        self.postgres_db = self.require_env("POSTGRES_DB")

    @classmethod
    def get(cls):
        """
        Get the singleton instance, loading from environment if not yet
        instantiated
        """
        if cls._instance is None:
            cls._allow_direct_init = True
            cls._instance = cls(os.environ)
            cls._allow_direct_init = False
        return cls._instance

    @classmethod
    def override(cls, env: dict):
        """
        Create singleton instance that
        overrides the environment variables with injected values
        """
        cls._allow_direct_init = True
        cls._instance = cls(env)
        cls._allow_direct_init = False

    @classmethod
    def reset(cls):
        cls._instance = None

    def get_postgres_connection_string(self, is_async = False):
        driver = "postgresql"
        if is_async:
            driver += "+asyncpg"
        return (f"{driver}://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}")

    def require_env(self, key: str, allow_none: bool = False):
        val = self.env.get(key)
        if val is None and not allow_none:
            raise ValueError(f"Environment variable {key} is not set")
        return val