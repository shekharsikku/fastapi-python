from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_EXPIRY: int = 3600
    REFRESH_EXPIRY: int = 3600 * 24

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


Config = Settings()
