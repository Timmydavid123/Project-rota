# app/api/__init__.py
"""API endpoints package"""

from app.api.endpoints import router as api_router

__all__ = ['api_router']