# app/routers/pages.py - Complete with all imports
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from pathlib import Path  # ← ADD THIS IMPORT
import json
import traceback
from datetime import datetime, timedelta

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    try:
        from app.services.analytics import AnalyticsService
        analytics = AnalyticsService()
        
        stats = analytics.get_system_stats()
        insights = analytics.get_recent_insights()
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "title": "Dashboard",
                "stats": stats,
                "insights": insights,
                "active_page": "dashboard"
            }
        )
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        traceback.print_exc()
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "title": "Dashboard",
                "stats": {'total_staff': 0, 'total_services': 0, 'active_shifts': 0, 'ai_enabled': False},
                "insights": [],
                "active_page": "dashboard",
                "error": str(e)
            }
        )

@router.get("/staff", response_class=HTMLResponse)
async def staff_list(request: Request):
    """Staff management page"""
    try:
        from app.services.ml_service import MLService
        service = MLService()
        
        staff_df = service.get_staff_data()
        staff_list = staff_df.to_dict('records') if not staff_df.empty else []
        
        return templates.TemplateResponse(
            "staff/list.html",
            {
                "request": request,
                "title": "Staff Management",
                "staff": staff_list,
                "active_page": "staff"
            }
        )
    except Exception as e:
        print(f"❌ Staff page error: {e}")
        traceback.print_exc()
        
        return templates.TemplateResponse(
            "staff/list.html",
            {
                "request": request,
                "title": "Staff Management",
                "staff": [],
                "error": str(e),
                "active_page": "staff"
            }
        )

@router.get("/staff/add", response_class=HTMLResponse)
async def add_staff_form(request: Request):
    """Add staff form"""
    return templates.TemplateResponse(
        "staff/add.html",
        {
            "request": request,
            "title": "Add Staff Member",
            "active_page": "staff"
        }
    )

@router.get("/services", response_class=HTMLResponse)
async def service_users(request: Request):
    """Service users page"""
    try:
        from app.services.ml_service import MLService
        service = MLService()
        
        services_df = service.get_service_data()
        services_list = services_df.to_dict('records') if not services_df.empty else []
        
        print(f"✅ Loaded {len(services_list)} service users")
        
        return templates.TemplateResponse(
            "services/list.html",
            {
                "request": request,
                "title": "Service Users",
                "services": services_list,
                "active_page": "services"
            }
        )
    except Exception as e:
        print(f"❌ Services page error: {e}")
        traceback.print_exc()
        
        return templates.TemplateResponse(
            "services/list.html",
            {
                "request": request,
                "title": "Service Users",
                "services": [],
                "error": str(e),
                "active_page": "services"
            }
        )

@router.get("/services/add", response_class=HTMLResponse)
async def add_service_form(request: Request):
    """Add service user form"""
    return templates.TemplateResponse(
        "services/add.html",
        {
            "request": request,
            "title": "Add Service User",
            "active_page": "services"
        }
    )

@router.get("/schedule", response_class=HTMLResponse)
async def schedule_view(request: Request, date: Optional[str] = None, generated: Optional[str] = None):
    """View schedule page"""
    try:
        from app.services.optimizer import OptimizerService
        
        optimizer = OptimizerService()
        schedule = optimizer.get_current_schedule(date)
        
        # Check if there's a newly generated schedule
        temp_file = Path('data') / 'temp_schedule.json'  # Now Path is defined
        show_success = generated == 'true'
        metrics = None
        
        if show_success and temp_file.exists():
            try:
                with open(temp_file, 'r') as f:
                    data = json.load(f)
                    schedule = data.get('schedule', schedule)
                    metrics = data.get('metrics')
                    print(f"✅ Loaded generated schedule with {len(schedule)} shifts")
            except Exception as e:
                print(f"⚠️ Error loading temp schedule: {e}")
        
        return templates.TemplateResponse(
            "schedule/view.html",
            {
                "request": request,
                "title": "Schedule",
                "schedule": schedule,
                "metrics": metrics,
                "selected_date": date,
                "show_success": show_success,
                "active_page": "schedule"
            }
        )
    except Exception as e:
        print(f"❌ Schedule page error: {e}")
        traceback.print_exc()
        
        return templates.TemplateResponse(
            "schedule/view.html",
            {
                "request": request,
                "title": "Schedule",
                "schedule": [],
                "metrics": None,
                "selected_date": date,
                "show_success": False,
                "error": str(e),
                "active_page": "schedule"
            }
        )

@router.get("/schedule/generate", response_class=HTMLResponse)
async def generate_schedule_form(request: Request):
    """Generate schedule form"""
    return templates.TemplateResponse(
        "schedule/generate.html",
        {
            "request": request,
            "title": "Generate Schedule",
            "default_start_date": datetime.now().strftime('%Y-%m-%d'),
            "num_days": 7,
            "use_ai": False,
            "ai_weight": 0.3,
            "active_page": "schedule"
        }
    )

@router.get("/schedule/calendar", response_class=HTMLResponse)
async def calendar_view(request: Request):
    """Calendar view page"""
    try:
        return templates.TemplateResponse(
            "schedule/calendar.html",
            {
                "request": request,
                "title": "Calendar View",
                "active_page": "schedule"
            }
        )
    except Exception as e:
        print(f"❌ Calendar page error: {e}")
        traceback.print_exc()
        
        return templates.TemplateResponse(
            "errors/500.html",
            {
                "request": request,
                "error": str(e),
                "active_page": "schedule"
            },
            status_code=500
        )

@router.get("/analytics", response_class=HTMLResponse)
async def analytics_dashboard(request: Request):
    """Analytics dashboard page"""
    try:
        from app.services.analytics import AnalyticsService
        analytics = AnalyticsService()
        
        coverage = analytics.analyze_coverage()
        utilization = analytics.analyze_utilization()
        insights = analytics.generate_insights()
        
        return templates.TemplateResponse(
            "analytics/dashboard.html",
            {
                "request": request,
                "title": "Analytics",
                "coverage": coverage,
                "utilization": utilization,
                "insights": insights,
                "active_page": "analytics"
            }
        )
    except Exception as e:
        print(f"❌ Analytics page error: {e}")
        traceback.print_exc()
        
        return templates.TemplateResponse(
            "analytics/dashboard.html",
            {
                "request": request,
                "title": "Analytics",
                "coverage": [],
                "utilization": [],
                "insights": [],
                "error": str(e),
                "active_page": "analytics"
            }
        )

@router.get("/analytics/coverage", response_class=HTMLResponse)
async def coverage_analytics(request: Request):
    """Coverage analysis page"""
    try:
        from app.services.analytics import AnalyticsService
        analytics = AnalyticsService()
        coverage = analytics.analyze_coverage()
        
        return templates.TemplateResponse(
            "analytics/coverage.html",
            {
                "request": request,
                "title": "Coverage Analysis",
                "coverage": coverage,
                "active_page": "analytics"
            }
        )
    except Exception as e:
        print(f"❌ Coverage page error: {e}")
        traceback.print_exc()
        
        return templates.TemplateResponse(
            "errors/500.html",
            {
                "request": request,
                "error": str(e),
                "active_page": "analytics"
            },
            status_code=500
        )

@router.get("/analytics/utilization", response_class=HTMLResponse)
async def utilization_analytics(request: Request):
    """Utilization analysis page"""
    try:
        from app.services.analytics import AnalyticsService
        analytics = AnalyticsService()
        utilization = analytics.analyze_utilization()
        
        return templates.TemplateResponse(
            "analytics/utilization.html",
            {
                "request": request,
                "title": "Staff Utilization",
                "utilization": utilization,
                "active_page": "analytics"
            }
        )
    except Exception as e:
        print(f"❌ Utilization page error: {e}")
        traceback.print_exc()
        
        return templates.TemplateResponse(
            "errors/500.html",
            {
                "request": request,
                "error": str(e),
                "active_page": "analytics"
            },
            status_code=500
        )

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Settings page"""
    import os
    
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "title": "Settings",
            "environment": os.getenv('ENVIRONMENT', 'development'),
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "active_page": "settings"
        }
    )

# API endpoints for AJAX calls
@router.get("/api/services")
async def api_get_services():
    """API endpoint to get all services"""
    try:
        from app.services.ml_service import MLService
        ml_service = MLService()
        services_df = ml_service.get_service_data()
        return services_df.to_dict('records')
    except Exception as e:
        print(f"❌ API services error: {e}")
        return []