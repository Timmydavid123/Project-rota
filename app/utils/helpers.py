# app/utils/helpers.py
from datetime import datetime, timedelta
import pandas as pd
import json
from pathlib import Path

def format_date(date_str, format='%Y-%m-%d'):
    """Format date string to desired format"""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime(format)
    except:
        return date_str

def get_week_dates(start_date=None):
    """Get list of dates for current week"""
    if start_date is None:
        start_date = datetime.now().date()
    elif isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    # Find Monday of the week
    monday = start_date - timedelta(days=start_date.weekday())
    
    # Generate week dates
    return [(monday + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]

def calculate_working_hours(schedule, staff_name=None):
    """Calculate total working hours from schedule"""
    if not schedule:
        return 0
    
    if staff_name:
        staff_shifts = [s for s in schedule if s.get('staff_assigned') == staff_name]
        return sum(s.get('hours', 0) for s in staff_shifts)
    
    return sum(s.get('hours', 0) for s in schedule)

def get_shift_color(support_ratio):
    """Get color code for shift based on support ratio"""
    colors = {
        1: '#28a745',  # Green
        2: '#ffc107',  # Yellow
        3: '#dc3545',  # Red
        4: '#6f42c1'   # Purple
    }
    return colors.get(support_ratio, '#6c757d')

def export_to_csv(data, filename):
    """Export data to CSV file"""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    return filename

def load_json_file(filepath):
    """Load JSON file safely"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        return None

def save_json_file(data, filepath):
    """Save data to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def validate_email(email):
    """Simple email validation"""
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Simple phone validation"""
    import re
    pattern = r'^[\d\s\-\+\(\)]{10,}$'
    return re.match(pattern, phone) is not None

def get_status_badge(status):
    """Get Bootstrap badge class for status"""
    badges = {
        'active': 'success',
        'inactive': 'secondary',
        'pending': 'warning',
        'completed': 'info',
        'cancelled': 'danger',
        'Good': 'success',
        'Warning': 'warning',
        'Critical': 'danger',
        'Over-utilized': 'danger',
        'Well-utilized': 'success',
        'Under-utilized': 'warning',
        'Idle': 'secondary'
    }
    return badges.get(status, 'secondary')