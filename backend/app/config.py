from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    token_encryption_key: str
    claim_signer_private_key: str
    chain_id: int
    driver_token_contract: str
    uber_client_id: str
    uber_client_secret: str
    uber_redirect_uri: str
    uber_scopes: str = "profile history"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
