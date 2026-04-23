# app/utils/validators.py
"""Validation utilities"""

from datetime import datetime
import re

def validate_staff_data(data):
    """Validate staff data"""
    errors = []
    
    # Required fields
    if not data.get('name'):
        errors.append('Name is required')
    
    if not data.get('role'):
        errors.append('Role is required')
    
    if not data.get('availability'):
        errors.append('Availability is required')
    
    # Validate max hours
    max_hours = data.get('max_hours', 0)
    if max_hours < 0 or max_hours > 168:
        errors.append('Max hours must be between 0 and 168')
    
    # Validate email if provided
    email = data.get('email')
    if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        errors.append('Invalid email format')
    
    # Validate phone if provided
    phone = data.get('phone')
    if phone and not re.match(r'^[\d\s\-\+\(\)]{10,}$', phone):
        errors.append('Invalid phone format')
    
    return errors

def validate_service_data(data):
    """Validate service user data"""
    errors = []
    
    # Required fields
    if not data.get('name'):
        errors.append('Service user name is required')
    
    support_ratio = data.get('support_ratio', 1)
    if support_ratio < 1 or support_ratio > 4:
        errors.append('Support ratio must be between 1 and 4')
    
    days_per_week = data.get('days_per_week', 5)
    if days_per_week < 1 or days_per_week > 7:
        errors.append('Days per week must be between 1 and 7')
    
    shift_duration = data.get('shift_duration', 8)
    if shift_duration < 1 or shift_duration > 24:
        errors.append('Shift duration must be between 1 and 24 hours')
    
    return errors

def validate_allocation_request(data):
    """Validate allocation request"""
    errors = []
    
    # Validate start date
    try:
        start_date = datetime.strptime(data.get('start_date', ''), '%Y-%m-%d')
        if start_date < datetime.now():
            errors.append('Start date cannot be in the past')
    except ValueError:
        errors.append('Invalid start date format. Use YYYY-MM-DD')
    
    # Validate number of days
    num_days = data.get('num_days', 7)
    if num_days < 1 or num_days > 30:
        errors.append('Number of days must be between 1 and 30')
    
    # Validate AI weight
    ai_weight = data.get('ai_weight', 0.3)
    if ai_weight < 0 or ai_weight > 1:
        errors.append('AI weight must be between 0 and 1')
    
    return errors

def sanitize_input(text):
    """Sanitize user input"""
    if not text:
        return text
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>]', '', text)
    
    return text.strip()