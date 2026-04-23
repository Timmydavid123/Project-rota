# app/routers/allocation.py - Fixed form handling
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
import traceback
import json
from pathlib import Path
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/generate")
async def generate_allocation(
    request: Request,
    start_date: str = Form(...),
    num_days: str = Form("7"),  # Accept as string, convert later
    use_ai: Optional[str] = Form(None),  # Checkbox returns "on" or None
    ai_weight: str = Form("0.3")  # Accept as string
):
    """Generate optimized allocation"""
    from app.services.optimizer import OptimizerService
    from app.services.ml_service import MLService
    
    try:
        # Convert form values
        start = datetime.strptime(start_date, '%Y-%m-%d')
        num_days_int = int(num_days)
        use_ai_bool = use_ai == "on"  # Checkbox returns "on" when checked
        ai_weight_float = float(ai_weight)
        
        print(f"\n{'='*50}")
        print(f"🚀 Generating allocation")
        print(f"{'='*50}")
        print(f"Start Date: {start_date}")
        print(f"Days: {num_days_int}")
        print(f"Use AI: {use_ai_bool}")
        print(f"AI Weight: {ai_weight_float}")
        
        # Run optimization
        optimizer = OptimizerService()
        
        result = optimizer.optimize_allocation(
            start_date=start,
            num_days=num_days_int,
            use_ai=use_ai_bool,
            ai_weight=ai_weight_float
        )
        
        if result.get('success'):
            print(f"✅ Allocation generated successfully!")
            print(f"   Total assignments: {result['metrics']['total_assignments']}")
            
            # Store schedule in a temporary file
            schedule_file = Path('data') / 'temp_schedule.json'
            schedule_file.parent.mkdir(exist_ok=True)
            with open(schedule_file, 'w') as f:
                json.dump({
                    'schedule': result['schedule'],
                    'metrics': result['metrics']
                }, f, indent=2)
            
            return RedirectResponse(
                url=f"/schedule?date={start_date}&generated=true",
                status_code=303
            )
        else:
            error_msg = result.get('error', 'Could not generate schedule. Check constraints.')
            print(f"❌ Allocation failed: {error_msg}")
            
            return templates.TemplateResponse(
                "schedule/generate.html",
                {
                    "request": request,
                    "error": error_msg,
                    "default_start_date": start_date,
                    "num_days": num_days_int,
                    "use_ai": use_ai_bool,
                    "ai_weight": ai_weight_float,
                    "active_page": "schedule"
                }
            )
            
    except ValueError as e:
        error_msg = f"Invalid form data: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        
        return templates.TemplateResponse(
            "schedule/generate.html",
            {
                "request": request,
                "error": error_msg,
                "default_start_date": datetime.now().strftime('%Y-%m-%d'),
                "num_days": 7,
                "use_ai": False,
                "ai_weight": 0.3,
                "active_page": "schedule"
            },
            status_code=400
        )
        
    except Exception as e:
        error_msg = f"Error generating allocation: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        
        return templates.TemplateResponse(
            "schedule/generate.html",
            {
                "request": request,
                "error": error_msg,
                "default_start_date": datetime.now().strftime('%Y-%m-%d'),
                "num_days": 7,
                "active_page": "schedule"
            },
            status_code=400
        )

@router.get("/api/schedule")
async def api_get_schedule(date: str = None, staff: str = None, limit: int = None):
    """API endpoint to get schedule data"""
    from app.services.optimizer import OptimizerService
    optimizer = OptimizerService()
    
    schedule = optimizer.get_current_schedule(date, staff)
    
    if limit:
        schedule = schedule[:limit]
    
    return schedule