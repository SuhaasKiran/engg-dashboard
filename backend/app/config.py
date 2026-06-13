from datetime import datetime, timedelta, timezone

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    github_token: str = ""
    github_owner: str = "PostHog"
    github_repo: str = "posthog"
    database_url: str = "postgresql+asyncpg://weave:weave@localhost:5432/weave"
    measurement_days: int = 120
    default_branch: str = "main"
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def measurement_start(self) -> datetime:
        return datetime.now(timezone.utc) - timedelta(days=self.measurement_days)

    @property
    def repo_full_name(self) -> str:
        return f"{self.github_owner}/{self.github_repo}"


settings = Settings()
