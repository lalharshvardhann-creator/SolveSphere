from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/solvesphere"
    APP_TITLE: str = "SolveSphere API"
    APP_DESCRIPTION: str = (
        "SolveSphere connects societal challenges in Jharkhand with Higher Education "
        "Institutions, industry and other innovation partners"
    )
    APP_VERSION: str = "1.0.0"


settings = Settings()
