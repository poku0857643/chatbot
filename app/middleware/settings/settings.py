from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from pathlib import Path
from typing import List

class Settings(BaseSettings):
    # Gemini API Configuration
    GEMINI_API_KEY: SecretStr
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "models/text-embedding-004"

    # CORS Configuration
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Upload Configuration
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: List[str] = [".pdf", ".txt", ".docx"]

    # RAG Configuration
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RESULTS: int = 5

    # Embedding Dimension (for text-embedding-004)
    EMBEDDING_DIMENSION: int = 768

    # Security Configuration
    RATE_LIMIT_CHAT: str = "10/minute"  # 10 chat requests per minute
    RATE_LIMIT_UPLOAD: str = "5/minute"  # 5 file uploads per minute
    MAX_MESSAGE_LENGTH: int = 4000  # Max characters in a chat message
    MAX_CONVERSATION_HISTORY: int = 20  # Max messages to keep in history
    ENABLE_SANITIZATION: bool = True  # Enable HTML/script sanitization

    # Cost Protection (Daily Limits Per IP)
    DAILY_CHAT_LIMIT_PER_IP: int = 100  # Max chat requests per day per IP
    DAILY_UPLOAD_LIMIT_PER_IP: int = 20  # Max uploads per day per IP
    DAILY_TOKEN_LIMIT_PER_IP: int = 10000  # Max tokens per day per IP (~10-20 conversations)

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent.parent / '.env',
        env_file_encoding='utf-8'
    )

config = Settings()