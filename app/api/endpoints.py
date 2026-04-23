# app/api/endpoints.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from datetime import datetime
import pandas as pd

from app.services.ml_service import MLService
from app.services.optimizer import OptimizerService
from app.services.analytics import AnalyticsService
from app.models.schemas import (
    StaffResponse, ServiceUserResponse, 
    AllocationRequest, AllocationResponse,
    AnalyticsResponse, InsightResponse
)

router = APIRouter()

# Staff endpoints
@router.get("/staff", response_model=List[StaffResponse])
async def get_all_staff():
    """Get all staff members"""
    ml_service = MLService()
    staff_df = ml_service.get_staff_data()
    return staff_df.to_dict('records')

@router.get("/staff/{staff_id}", response_model=StaffResponse)
async def get_staff(staff_id: int):
    """Get staff member by ID"""
    ml_service = MLService()
    staff_df = ml_service.get_staff_data()
    staff = staff_df[staff_df['Employee ID'] == staff_id]
    if staff.empty:
        raise HTTPException(status_code=404, detail="Staff not found")
    return staff.iloc[0].to_dict()

@router.post("/staff")
async def create_staff(staff_data: dict):
    """Create new staff member"""
    ml_service = MLService()
    staff_df = ml_service.get_staff_data()
    
    # Generate new ID
    new_id = staff_df['Employee ID'].max() + 1 if not staff_df.empty else 1
    staff_data['Employee ID'] = new_id
    
    # Append and save
    new_staff = pd.DataFrame([staff_data])
    staff_df = pd.concat([staff_df, new_staff], ignore_index=True)
    staff_df.to_csv('data/sample_staff.csv', index=False)
    
    return {"message": "Staff created", "id": new_id}

@router.put("/staff/{staff_id}")
async def update_staff(staff_id: int, staff_data: dict):
    """Update staff member"""
    ml_service = MLService()
    staff_df = ml_service.get_staff_data()
    
    mask = staff_df['Employee ID'] == staff_id
    if not mask.any():
        raise HTTPException(status_code=404, detail="Staff not found")
    
    for key, value in staff_data.items():
        if key in staff_df.columns:
            staff_df.loc[mask, key] = value
    
    staff_df.to_csv('data/sample_staff.csv', index=False)
    return {"message": "Staff updated"}

@router.delete("/staff/{staff_id}")
async def delete_staff(staff_id: int):
    """Delete staff member"""
    ml_service = MLService()
    staff_df = ml_service.get_staff_data()
    
    staff_df = staff_df[staff_df['Employee ID'] != staff_id]
    staff_df.to_csv('data/sample_staff.csv', index=False)
    
    return {"message": "Staff deleted"}

# Service User endpoints
@router.get("/api/services")
async def api_get_services():
    """API endpoint to get all services"""
    from app.services.ml_service import MLService
    
    try:
        ml_service = MLService()
        services_df = ml_service.get_service_data()
        return services_df.to_dict('records')
    except Exception as e:
        print(f"Error getting services: {e}")
        return []

@router.get("/services/{service_id}")
async def get_service(service_id: int):
    """Get service user by index"""
    ml_service = MLService()
    service_df = ml_service.get_service_data()
    if service_id >= len(service_df):
        raise HTTPException(status_code=404, detail="Service user not found")
    return service_df.iloc[service_id].to_dict()

# Allocation endpoints
@router.post("/allocate", response_model=AllocationResponse)
async def generate_allocation(request: AllocationRequest):
    """Generate optimized staff allocation"""
    optimizer = OptimizerService()
    
    result = optimizer.optimize_allocation(
        start_date=datetime.strptime(request.start_date, '%Y-%m-%d'),
        num_days=request.num_days,
        use_ai=request.use_ai,
        ai_weight=request.ai_weight
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Optimization failed'))
    
    return result

@router.get("/schedule")
async def get_schedule(date: Optional[str] = None, staff: Optional[str] = None):
    """Get current schedule"""
    optimizer = OptimizerService()
    schedule = optimizer.get_current_schedule(date, staff)
    return schedule

# Analytics endpoints
@router.get("/analytics/coverage")
async def get_coverage_analytics():
    """Get coverage analysis"""
    analytics = AnalyticsService()
    return analytics.analyze_coverage()

@router.get("/analytics/utilization")
async def get_utilization_analytics():
    """Get staff utilization analysis"""
    analytics = AnalyticsService()
    return analytics.analyze_utilization()

@router.get("/analytics/insights", response_model=List[InsightResponse])
async def get_insights():
    """Get AI-generated insights"""
    analytics = AnalyticsService()
    return analytics.generate_insights()

# ML endpoints
@router.post("/ml/train")
async def train_models():
    """Train ML models"""
    ml_service = MLService()
    result = ml_service.train_all_models()
    
    if 'error' in result:
        raise HTTPException(status_code=500, detail=result['error'])
    
    return result

@router.get("/ml/status")
async def get_ml_status():
    """Get ML models status"""
    ml_service = MLService()
    return {
        "trained": ml_service.is_trained,
        "models_loaded": ml_service.availability_model is not None
    }

# Health check
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    ml_service = MLService()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ai_enabled": ml_service.is_trained
    }

@router.post("/api/ml/train")
async def train_models():
    """Train ML models"""
    from app.services.ml_service import MLService
    
    try:
        ml_service = MLService()
        result = ml_service.train_all_models()
        
        if 'error' in result:
            return JSONResponse(
                status_code=500,
                content={"error": result['error']}
            )
        
        return {
            "success": True,
            "message": "Models trained successfully",
            "scores": {
                "availability": result.get('availability_score', 0),
                "preference": result.get('preference_score', 0)
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )