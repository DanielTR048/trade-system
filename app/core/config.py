from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Variáveis do banco de dados lidas do .env
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()