from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "VMC Bridge API"
    version: str = "0.1.0"
    debug: bool = True

    database_url: str | None = None
    
    # JWT Authentication Settings
    secret_key: str = "your-secret-key-change-in-production-min-32-chars-long"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env that aren't defined in Settings


def get_settings() -> Settings:
    return Settings()
