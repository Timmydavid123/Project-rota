# app/main.py (Update the health endpoint path)
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
import os
from pathlib import Path

from app.routers import pages, staff, allocation, analytics
from app.services.ml_service import MLService
from app.utils.data_generator import ensure_data_exists

# Initialize ML service
ml_service = MLService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("🚀 Starting Staff Rota System...")
    ensure_data_exists()
    
    # Try to load ML models
    if ml_service.load_models():
        print("✅ ML models loaded successfully")
    else:
        print("⚠️ No ML models found - AI features disabled")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Staff Rota Management System",
    description="AI-Enhanced Staff Allocation System for Care Services",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(pages.router)
app.include_router(staff.router, prefix="/staff", tags=["Staff"])
app.include_router(allocation.router, prefix="/allocation", tags=["Allocation"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

# API routes - FIXED PATH
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "rota-system",
        "ai_enabled": ml_service.is_trained
    }

# Also add root-level health for Docker
@app.get("/health")
async def root_health_check():
    """Root health check endpoint"""
    return {
        "status": "healthy",
        "service": "rota-system",
        "ai_enabled": ml_service.is_trained
    }

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    from app.services.analytics import AnalyticsService
    analytics_service = AnalyticsService()
    return analytics_service.get_system_stats()

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=404,
            content={"detail": "Not found"}
        )
    return templates.TemplateResponse(
        "errors/404.html",
        {"request": request},
        status_code=404
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    return templates.TemplateResponse(
        "errors/500.html",
        {"request": request},
        status_code=500
    )