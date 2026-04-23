# config.py
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    app_name: str = "Staff Rota AI System"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Paths
    data_path: str = "data"
    models_path: str = "models"
    logs_path: str = "logs"
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    api_key: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///rota.db"
    
    # AI settings
    ai_enabled: bool = True
    default_ai_weight: float = 0.3
    
    # Optimization settings
    max_optimization_time: int = 120  # seconds
    solver_threads: int = 4
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()