from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "VMC Bridge API"
    version: str = "0.1.0"
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    return Settings()
