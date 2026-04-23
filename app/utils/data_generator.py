# app/utils/data_generator.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

def ensure_data_exists():
    """Ensure all required data files exist"""
    data_path = Path('data')
    data_path.mkdir(exist_ok=True)
    
    # Check and create staff data
    if not (data_path / 'sample_staff.csv').exists():
        create_sample_staff(data_path)
    
    # Check and create service user data
    if not (data_path / 'service_users.csv').exists():
        create_sample_services(data_path)
    
    # Check and create historical data
    if not (data_path / 'historical_shifts.csv').exists():
        create_sample_historical(data_path)
    
    print("✅ Data files verified")

def create_sample_staff(data_path):
    """Create sample staff data"""
    staff_data = {
        'Employee ID': list(range(1, 16)),
        'Employee Name': [
            'John Smith', 'Sarah Johnson', 'Michael Brown', 'Emma Wilson',
            'David Lee', 'Lisa Anderson', 'James Taylor', 'Maria Garcia',
            'Robert Martin', 'Patricia White', 'Thomas Moore', 'Jennifer Hall',
            'William Clark', 'Elizabeth Lewis', 'Richard Walker'
        ],
        'Role': ['Senior Support Worker'] * 5 + ['Support Worker'] * 10,
        'Department': ['Care Team'] * 15,
        'Availability': [
            'Mon;Tue;Wed;Thu;Fri', 'Mon;Wed;Fri;Sat;Sun',
            'Tue;Wed;Thu;Fri;Sat', 'Mon;Tue;Wed;Thu;Fri',
            'Wed;Thu;Fri;Sat;Sun', 'Mon;Tue;Thu;Fri;Sat',
            'Mon;Wed;Fri;Sat;Sun', 'Tue;Thu;Sat;Sun',
            'Mon;Tue;Wed;Thu;Fri', 'Mon;Wed;Fri;Sat',
            'Tue;Wed;Thu;Fri;Sat', 'Mon;Tue;Wed;Thu;Fri',
            'Wed;Thu;Fri;Sat;Sun', 'Mon;Tue;Thu;Fri;Sat',
            'Mon;Wed;Fri;Sat;Sun'
        ],
        'Shift Preference': [
            'Morning', 'Evening', 'Morning', 'Flexible', 'Evening',
            'Morning', 'Flexible', 'Evening', 'Morning', 'Evening',
            'Morning', 'Flexible', 'Evening', 'Morning', 'Flexible'
        ],
        'Max Hours/Week': [40] * 15,
        'Experience_Years': [8, 6, 10, 4, 7, 3, 5, 9, 2, 4, 6, 3, 8, 5, 2],
        'Special_Skills': [
            'Dementia Care', 'Medication', 'Palliative Care',
            'Learning Disabilities', 'Mental Health', 'Physical Disabilities',
            'Dementia Care', 'Medication', 'Learning Disabilities',
            'Palliative Care', 'Mental Health', 'Physical Disabilities',
            'Dementia Care', 'Medication', 'Learning Disabilities'
        ]
    }
    
    df = pd.DataFrame(staff_data)
    df.to_csv(data_path / 'sample_staff.csv', index=False)
    print(f"✅ Created staff data: {len(df)} records")
    return df

def create_sample_services(data_path):
    """Create sample service user data"""
    service_data = {
        'Service User': [
            'Alice Johnson', 'Bob Williams', 'Carol Davis', 'David Miller',
            'Eva Brown', 'Frank Wilson', 'Grace Taylor', 'Henry Anderson',
            'Irene Thomas', 'Jack Martin'
        ],
        'Primary_Shift': [
            '09:00-17:00', '08:00-16:00', '10:00-18:00', '09:00-17:00',
            '08:00-20:00', '09:00-17:00', '10:00-18:00', '08:00-16:00',
            '09:00-17:00', '08:00-20:00'
        ],
        'Support_Ratio': [2, 1, 2, 1, 3, 2, 1, 2, 1, 3],
        'Days_Per_Week': [5, 7, 5, 6, 7, 5, 7, 5, 6, 7],
        'Shift_Duration_Hours': [8, 8, 8, 8, 12, 8, 8, 8, 8, 12],
        'Location': [
            'North Zone', 'South Zone', 'East Zone', 'West Zone', 'North Zone',
            'South Zone', 'East Zone', 'West Zone', 'North Zone', 'South Zone'
        ],
        'Weekly_Required_Hours': [80, 56, 80, 48, 252, 80, 56, 80, 48, 252],
        'Care_Level': [
            'High', 'Medium', 'High', 'Medium', 'Critical',
            'High', 'Medium', 'High', 'Medium', 'Critical'
        ],
        'Special_Requirements': [
            'Hoist required', 'None', 'PEG feeding', 'Wheelchair access',
            'Ventilator care', 'Hoist required', 'None', 'PEG feeding',
            'Wheelchair access', 'Ventilator care'
        ]
    }
    
    df = pd.DataFrame(service_data)
    df.to_csv(data_path / 'service_users.csv', index=False)
    print(f"✅ Created service user data: {len(df)} records")
    return df

def create_sample_historical(data_path):
    """Create sample historical shift data"""
    historical = []
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)
    
    staff_names = [
        'John Smith', 'Sarah Johnson', 'Michael Brown', 'Emma Wilson',
        'David Lee', 'Lisa Anderson', 'James Taylor', 'Maria Garcia'
    ]
    
    service_users = [
        'Alice Johnson', 'Bob Williams', 'Carol Davis', 'David Miller',
        'Eva Brown', 'Frank Wilson'
    ]
    
    for i in range(90):
        date = start_date + timedelta(days=i)
        
        # Generate 8-12 shifts per day
        for _ in range(np.random.randint(8, 13)):
            staff = np.random.choice(staff_names)
            shift = np.random.choice(['Morning', 'Afternoon', 'Evening'])
            
            historical.append({
                'Employee': staff,
                'Date': date.strftime('%Y-%m-%d'),
                'Shift': shift,
                'Worked': 1,
                'Hours': np.random.choice([6, 7, 8, 9, 10]),
                'Preferred': np.random.choice(['Y', 'N'], p=[0.7, 0.3]),
                'Role': 'Support Worker' if staff in staff_names[4:] else 'Senior Support Worker',
                'Performance_Score': np.random.choice([3, 4, 5], p=[0.2, 0.5, 0.3]),
                'Service_User': np.random.choice(service_users)
            })
    
    df = pd.DataFrame(historical)
    df.to_csv(data_path / 'historical_shifts.csv', index=False)
    print(f"✅ Created historical data: {len(df)} records")
    return df

def ensure_directories():
    """Create all required directories"""
    directories = ['data', 'models', 'logs', 'app/static/css', 'app/static/js', 'app/static/img']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")