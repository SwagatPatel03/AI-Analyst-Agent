from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Application
    APP_NAME: str
    DEBUG: bool = False
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str
    
    # AI APIs
    GROQ_API_KEY: str
    GEMINI_API_KEY: str = "not-configured"  # Optional
    
    # Email - Mailgun (Primary)
    MAILGUN_API_KEY: str = "not-configured"  # Optional
    MAILGUN_DOMAIN: str = "not-configured"  # Optional
    
    # Email - SendGrid (Alternative)
    SENDGRID_API_KEY: str = "not-configured"  # Optional
    FROM_EMAIL: str = "noreply@aianalyst.com"  # Optional
    
    # Email - Extra fields (ignore if present)
    SENDING_KEY: str = "not-configured"  # Optional - Mailgun sending key
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 50000000
    ALLOWED_EXTENSIONS: str = "pdf,xlsx,xls,csv"
    
    # CORS
    CORS_ORIGINS: str
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
