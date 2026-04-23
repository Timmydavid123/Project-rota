# app/routers/staff.py
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
import pandas as pd

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/add")
async def add_staff(
    request: Request,
    name: str = Form(...),
    role: str = Form(...),
    department: str = Form(...),
    availability: str = Form(...),
    shift_preference: str = Form(...),
    max_hours: int = Form(...),
    experience: int = Form(0),
    skills: str = Form("")
):
    """Handle staff addition form submission"""
    from app.services.ml_service import MLService
    service = MLService()
    
    try:
        # Load existing staff
        staff_df = service.get_staff_data()
        
        # Create new staff record
        new_staff = {
            'Employee ID': len(staff_df) + 1,
            'Employee Name': name,
            'Role': role,
            'Department': department,
            'Availability': availability,
            'Shift Preference': shift_preference,
            'Max Hours/Week': max_hours,
            'Experience_Years': experience,
            'Special_Skills': skills
        }
        
        # Append and save
        staff_df = pd.concat([staff_df, pd.DataFrame([new_staff])], ignore_index=True)
        staff_df.to_csv('data/sample_staff.csv', index=False)
        
        return RedirectResponse(url="/staff", status_code=303)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{staff_id}/edit", response_class=HTMLResponse)
async def edit_staff_form(request: Request, staff_id: int):
    """Edit staff form"""
    from app.services.ml_service import MLService
    service = MLService()
    
    staff_df = service.get_staff_data()
    staff = staff_df[staff_df['Employee ID'] == staff_id].to_dict('records')
    
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    return templates.TemplateResponse(
        "staff/edit.html",
        {
            "request": request,
            "title": "Edit Staff",
            "staff": staff[0],
            "active_page": "staff"
        }
    )

@router.post("/{staff_id}/update")
async def update_staff(
    request: Request,
    staff_id: int,
    name: str = Form(...),
    role: str = Form(...),
    # ... other fields
):
    """Update staff member"""
    from app.services.ml_service import MLService
    service = MLService()
    
    staff_df = service.get_staff_data()
    
    # Update staff record
    mask = staff_df['Employee ID'] == staff_id
    staff_df.loc[mask, 'Employee Name'] = name
    staff_df.loc[mask, 'Role'] = role
    # ... update other fields
    
    staff_df.to_csv('data/sample_staff.csv', index=False)
    
    return RedirectResponse(url="/staff", status_code=303)

@router.get("/{staff_id}/delete")
async def delete_staff(staff_id: int):
    """Delete staff member"""
    from app.services.ml_service import MLService
    service = MLService()
    
    staff_df = service.get_staff_data()
    staff_df = staff_df[staff_df['Employee ID'] != staff_id]
    staff_df.to_csv('data/sample_staff.csv', index=False)
    
    return RedirectResponse(url="/staff", status_code=303)

# API Endpoints for AJAX calls
@router.get("/api/list")
async def api_get_staff():
    """API endpoint to get staff list"""
    from app.services.ml_service import MLService
    service = MLService()
    
    staff_df = service.get_staff_data()
    return staff_df.to_dict('records')

@router.get("/api/{staff_id}")
async def api_get_staff_detail(staff_id: int):
    """API endpoint to get staff details"""
    from app.services.ml_service import MLService
    service = MLService()
    
    staff_df = service.get_staff_data()
    staff = staff_df[staff_df['Employee ID'] == staff_id].to_dict('records')
    
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    return staff[0]