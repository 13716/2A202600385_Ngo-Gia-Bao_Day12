from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Production AI Agent"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Security & AI
    AGENT_API_KEY: str = "super-secret-key-123"
    GEMINI_API_KEY: str = "" 
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Rate Limiting & Cost Guard
    RATE_LIMIT_PER_MINUTE: int = 5
    MONTHLY_BUDGET_USD: float = 10.0
    
    # LLM Mock Config
    LLM_MODEL: str = "mock-gpt-4"

    class Config:
        env_file = ".env"

settings = Settings()
