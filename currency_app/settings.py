from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    version: str = "0.1.0"

    database_dsn: SecretStr = SecretStr(
        "postgresql://alice:xyz@localhost:5432/currency_app"
    )

    nbp_api_url: str = "https://api.nbp.pl/api/exchangerates/tables/A/"


settings = Settings()
