from pathlib import Path

from pydantic_settings import BaseSettings

_BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_env: str = "development"
    debug: bool = True

    postgres_host: str = ""
    postgres_port: int = 5432
    postgres_user: str = ""
    postgres_password: str = ""
    postgres_db: str = ""

    openrouter_api_key: str = ""
    openrouter_model: str = "nvidia/nemotron-3-ultra-550b-a55b:free"
    openrouter_fallback_models: list[str] = [
        "meta-llama/llama-3.3-70b-instruct:free",
        "google/gemini-2.0-flash-exp:free",
    ]
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    jwt_secret: str = "autoexpert-dev-secret-change-in-production-2025"

    @property
    def database_url(self) -> str:
        if self.postgres_host and self.postgres_user:
            return (
                f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )
        db_path = _BACKEND_DIR / "database" / "chatbot.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite+aiosqlite:///{db_path}"

    @property
    def database_url_sync(self) -> str:
        if self.postgres_host and self.postgres_user:
            return (
                f"postgresql://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )
        db_path = _BACKEND_DIR / "database" / "chatbot.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db_path}"

    @property
    def is_sqlite(self) -> bool:
        return not (self.postgres_host and self.postgres_user)

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    def model_post_init(self, __context: object) -> None:
        if self.app_env == "production":
            insecure_defaults = {
                "",
                "autoexpert-dev-secret-change-in-production-2025",
                "change-me",
                "secret",
                "jwt-secret",
            }
            if self.jwt_secret in insecure_defaults:
                raise ValueError(
                    "jwt_secret must be set to a secure value in production. "
                    "Set the JWT_SECRET environment variable."
                )


settings = Settings()
