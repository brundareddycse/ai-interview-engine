from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App
    app_name: str = "InterviewPro API"
    debug: bool = False
    environment: str = "development"
    
    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Database
    database_url: str = "postgresql://user:password@localhost/interviewpro"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    
    # Interview Config
    default_interview_duration: int = 45  # minutes
    question_pool_size: int = 100
    min_questions: int = 5
    max_questions: int = 20
    
    # Scoring
    termination_threshold: float = 0.8  # Exit if confidence > 80%
    performance_threshold: float = 0.5  # Minimum to pass
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
