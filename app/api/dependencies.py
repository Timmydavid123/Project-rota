# app/api/dependencies.py
from functools import lru_cache
from app.services.ml_service import MLService
from app.services.optimizer import OptimizerService
from app.services.analytics import AnalyticsService

@lru_cache()
def get_ml_service():
    """Dependency for ML service"""
    return MLService()

@lru_cache()
def get_optimizer_service():
    """Dependency for optimizer service"""
    return OptimizerService()

@lru_cache()
def get_analytics_service():
    """Dependency for analytics service"""
    return AnalyticsService()

def verify_api_key(api_key: str):
    """Verify API key (for future authentication)"""
    # Implement API key verification
    return True