# app/models/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime

class StaffResponse(BaseModel):
    """Staff member response model"""
    id: Optional[int] = Field(None, alias='Employee ID')
    name: str = Field(..., alias='Employee Name')
    role: str = Field(..., alias='Role')
    department: Optional[str] = Field(None, alias='Department')
    availability: str = Field(..., alias='Availability')
    shift_preference: str = Field(..., alias='Shift Preference')
    max_hours: int = Field(..., alias='Max Hours/Week')
    experience_years: Optional[int] = Field(None, alias='Experience_Years')
    skills: Optional[str] = Field(None, alias='Special_Skills')
    
    class Config:
        populate_by_name = True

class ServiceUserResponse(BaseModel):
    """Service user response model"""
    name: str = Field(..., alias='Service User')
    primary_shift: str = Field(..., alias='Primary_Shift')
    support_ratio: int = Field(..., alias='Support_Ratio')
    days_per_week: int = Field(..., alias='Days_Per_Week')
    shift_duration: int = Field(..., alias='Shift_Duration_Hours')
    location: Optional[str] = Field(None, alias='Location')
    weekly_hours: int = Field(..., alias='Weekly_Required_Hours')
    care_level: Optional[str] = Field(None, alias='Care_Level')
    special_requirements: Optional[str] = Field(None, alias='Special_Requirements')
    
    class Config:
        populate_by_name = True

class AllocationRequest(BaseModel):
    """Allocation request model"""
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    num_days: int = Field(7, ge=1, le=30, description="Number of days to schedule")
    use_ai: bool = Field(True, description="Use AI recommendations")
    ai_weight: float = Field(0.3, ge=0.0, le=1.0, description="AI influence weight")

class ShiftAssignment(BaseModel):
    """Shift assignment model"""
    date: str
    service_user: str
    staff_assigned: str
    shift: str
    hours: int
    support_ratio: int
    location: Optional[str] = None

class AllocationMetrics(BaseModel):
    """Allocation metrics model"""
    total_assignments: int
    unique_staff_used: int
    unique_services: int
    total_hours: int
    avg_hours_per_staff: float

class AllocationResponse(BaseModel):
    """Allocation response model"""
    success: bool
    schedule: List[ShiftAssignment]
    metrics: AllocationMetrics
    status: str

class InsightResponse(BaseModel):
    """AI insight response model"""
    type: str
    severity: str
    message: str
    recommendation: Optional[str] = None

class AnalyticsResponse(BaseModel):
    """Analytics response model"""
    coverage: List[Dict[str, Any]]
    utilization: List[Dict[str, Any]]
    insights: List[InsightResponse]
    stats: Dict[str, Any]