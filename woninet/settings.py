from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    woninet_database_url: str

    model_config = SettingsConfigDict(env_file=".env")


def get_settings() -> Settings:
    """
    Load the application settings from the environment.

    Returns:
        Settings: The validated settings instance.
    """
    settings = Settings()
    return settings
