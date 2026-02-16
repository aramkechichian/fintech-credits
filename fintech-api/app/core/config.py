from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    app_name: str = "fintech-api"
    env: str = "dev"
    port: int = 8000
    
    # MongoDB settings
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    mongodb_db_name: str = "fintech-db"
    
    # JWT settings
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 360  # 6 hours

    model_config = SettingsConfigDict(env_file=".env", env_prefix="FINTECH_", extra="ignore")

settings = Settings()
