from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Job Tracker API"
    ENV: str = "local"

    # secrets with safe defaults for local/dev/test
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # credentials for a PostgreSQL database; optional for simple setups/tests
    POSTGRES_HOST: str | None = None
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str | None = None
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None

    # you can override the entire URL directly if you prefer
    DATABASE_URL: str | None = None

    @property
    def database_url(self) -> str:
        """Return a SQLAlchemy-compatible URL.

        Priority:
        1. ``DATABASE_URL`` env variable
        2. sqlite memory when running tests
        3. build a PostgreSQL url from the individual settings
        4. fallback to a local sqlite file (``./db.sqlite3``)
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL

        if self.ENV == "test":
            return "sqlite:///:memory:"

        if self.POSTGRES_HOST and self.POSTGRES_DB and self.POSTGRES_USER and self.POSTGRES_PASSWORD:
            return (
                f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

        # default for local development without PostgreSQL
        return "sqlite:///./db.sqlite3"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
