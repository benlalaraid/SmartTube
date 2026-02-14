import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart YouTube Downloader"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DOWNLOAD_DIR: str = os.path.join(os.getcwd(), "downloads")
    
    # RAG Settings
    CHROMA_PERSIST_DIR: str = os.path.join(os.getcwd(), "chroma_db")
    HF_API_TOKEN: str = os.getenv("HF_API_TOKEN", "")
    
    class Config:
        env_file = ".env"

settings = Settings()

# Ensure download directory exists
os.makedirs(settings.DOWNLOAD_DIR, exist_ok=True)
