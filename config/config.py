from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    TOKEN: str
    PROXY: str
    PROXY_ROTATION: str

    #метод для возвращения строки подключения к async БД
    @property
    def database_url_aisqlite(self) -> str:
        return f"sqlite+aiosqlite:///database/database.db"
    
    model_config = SettingsConfigDict(env_file="config/.env",extra="ignore")

settings = Settings()