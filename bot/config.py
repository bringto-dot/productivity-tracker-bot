from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str
    admin_ids: str = ""
    timezone: str = "Europe/Moscow"
    db_path: str = "bot.db"
    default_lang: str = "ru"

    @property
    def db_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.db_path}"

    @property
    def admin_id_list(self) -> set[int]:
        return {int(part.strip()) for part in self.admin_ids.split(",") if part.strip()}


settings = Settings()
