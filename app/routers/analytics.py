# app/routers/analytics.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.services.analytics import AnalyticsService

router = APIRouter()
analytics_service = AnalyticsService()

@router.get("/api/coverage")
async def api_coverage():
    """API endpoint for coverage analysis"""
    coverage = analytics_service.analyze_coverage()
    return JSONResponse(content=coverage)

@router.get("/api/utilization")
async def api_utilization():
    """API endpoint for utilization analysis"""
    utilization = analytics_service.analyze_utilization()
    return JSONResponse(content=utilization)

@router.get("/api/insights")
async def api_insights():
    """API endpoint for AI insights"""
    insights = analytics_service.generate_insights()
    return JSONResponse(content=insights)

@router.get("/api/stats")
async def api_stats():
    """API endpoint for system statistics"""
    stats = analytics_service.get_system_stats()
    return JSONResponse(content=stats)