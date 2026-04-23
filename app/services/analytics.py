# app/services/analytics.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
import math

class AnalyticsService:
    def __init__(self):
        self.data_path = Path('data')
        self.schedule_file = self.data_path / 'current_schedule.json'
    
    def get_system_stats(self):
        """Get overall system statistics"""
        from app.services.ml_service import MLService
        
        ml_service = MLService()
        staff_df = ml_service.get_staff_data()
        service_df = ml_service.get_service_data()
        
        schedule = self._load_schedule()
        
        # Calculate support ratio distribution
        if 'Support Ratio' in service_df.columns:
            ratio_counts = service_df['Support Ratio'].value_counts().to_dict()
            support_ratios = [
                {'ratio': int(ratio) if not pd.isna(ratio) else 0, 
                 'count': int(count) if not pd.isna(count) else 0}
                for ratio, count in ratio_counts.items()
            ]
        else:
            support_ratios = []
        
        # Calculate total weekly hours - handle NaN
        if 'Weekly Required Hours' in service_df.columns:
            total_weekly_hours = service_df['Weekly Required Hours'].fillna(0).sum()
            total_weekly_hours = int(total_weekly_hours) if not pd.isna(total_weekly_hours) else 0
        else:
            total_weekly_hours = 0
        
        # Calculate average experience - handle NaN
        if 'Experience_Years' in staff_df.columns:
            avg_experience = staff_df['Experience_Years'].fillna(0).mean()
            avg_experience = round(float(avg_experience), 1) if not pd.isna(avg_experience) else 0.0
        else:
            avg_experience = 0.0
        
        # Clean any NaN/Inf values from the result
        result = {
            'total_staff': self._clean_value(len(staff_df)),
            'total_services': self._clean_value(len(service_df)),
            'active_shifts': self._clean_value(len(schedule)),
            'ai_enabled': bool(ml_service.is_trained),
            'support_ratios': support_ratios,
            'total_weekly_hours': self._clean_value(total_weekly_hours),
            'avg_experience_years': self._clean_value(avg_experience)
        }
        
        return result
    
    def analyze_coverage(self):
        """Analyze service coverage"""
        service_df = self._load_service_data()
        schedule = self._load_schedule()
        
        if schedule:
            schedule_df = pd.DataFrame(schedule)
        else:
            schedule_df = pd.DataFrame()
        
        coverage_analysis = []
        
        for _, service in service_df.iterrows():
            service_name = str(service.get('Service User', 'Unknown'))
            required_ratio = self._safe_int(service.get('Support Ratio', 1))
            days_required = self._safe_int(service.get('Days/Week', 5))
            
            if not schedule_df.empty and 'service_user' in schedule_df.columns:
                service_schedule = schedule_df[schedule_df['service_user'] == service_name]
                days_covered = len(service_schedule)
                coverage_pct = (days_covered / max(days_required, 1)) * 100
            else:
                days_covered = 0
                coverage_pct = 0
            
            # Clean values
            coverage_pct = self._clean_value(coverage_pct)
            
            coverage_analysis.append({
                'service_user': service_name,
                'required_ratio': required_ratio,
                'days_covered': days_covered,
                'days_required': days_required,
                'coverage_percentage': round(coverage_pct, 1),
                'status': 'Good' if coverage_pct >= 90 else 'Warning' if coverage_pct >= 70 else 'Critical'
            })
        
        return coverage_analysis
    
    def analyze_utilization(self):
        """Analyze staff utilization"""
        staff_df = self._load_staff_data()
        schedule = self._load_schedule()
        
        utilization = []
        
        for _, staff in staff_df.iterrows():
            staff_name = str(staff.get('Employee Name', 'Unknown'))
            role = str(staff.get('Role', 'N/A'))
            max_hours = self._safe_int(staff.get('Max Hours/Week', 40))
            
            if schedule:
                staff_schedule = [s for s in schedule if s.get('staff_assigned') == staff_name]
                assigned_hours = sum(s.get('hours', 0) for s in staff_schedule)
            else:
                assigned_hours = 0
            
            utilization_rate = (assigned_hours / max_hours * 100) if max_hours > 0 else 0
            utilization_rate = self._clean_value(utilization_rate)
            
            # Determine status
            if utilization_rate > 95:
                status = 'Over-utilized'
                color = 'danger'
            elif utilization_rate > 70:
                status = 'Well-utilized'
                color = 'success'
            elif utilization_rate > 30:
                status = 'Under-utilized'
                color = 'warning'
            else:
                status = 'Idle'
                color = 'secondary'
            
            utilization.append({
                'staff_name': staff_name,
                'role': role,
                'assigned_hours': assigned_hours,
                'max_hours': max_hours,
                'utilization_rate': round(utilization_rate, 1),
                'status': status,
                'color': color,
                'available_hours': max_hours - assigned_hours
            })
        
        return utilization
    
    def generate_insights(self):
        """Generate AI-powered insights"""
        insights = []
        
        try:
            coverage = self.analyze_coverage()
            utilization = self.analyze_utilization()
            
            # Coverage insights
            low_coverage = [c for c in coverage if c['coverage_percentage'] < 90]
            if low_coverage:
                for item in low_coverage[:3]:
                    insights.append({
                        'type': 'Coverage Gap',
                        'severity': 'warning' if item['coverage_percentage'] >= 70 else 'danger',
                        'message': f"{item['service_user']} has {item['coverage_percentage']}% coverage",
                        'recommendation': f"Consider adding staff for {item['service_user']}"
                    })
            
            # Utilization insights
            over_utilized = [u for u in utilization if u['status'] == 'Over-utilized']
            if over_utilized:
                for staff in over_utilized[:2]:
                    insights.append({
                        'type': 'Workload',
                        'severity': 'warning',
                        'message': f"{staff['staff_name']} is at {staff['utilization_rate']}% utilization",
                        'recommendation': "Consider redistributing workload"
                    })
            
            under_utilized = [u for u in utilization if u['status'] in ['Under-utilized', 'Idle']]
            if len(under_utilized) > 3:
                insights.append({
                    'type': 'Capacity',
                    'severity': 'info',
                    'message': f"{len(under_utilized)} staff members have available capacity",
                    'recommendation': "Consider increasing their assignments"
                })
            
            # Overall system health
            avg_utilization = np.mean([u['utilization_rate'] for u in utilization]) if utilization else 0
            avg_coverage = np.mean([c['coverage_percentage'] for c in coverage]) if coverage else 0
            
            # Clean values
            avg_utilization = self._clean_value(avg_utilization)
            avg_coverage = self._clean_value(avg_coverage)
            
            insights.append({
                'type': 'System Health',
                'severity': 'success' if avg_coverage > 90 else 'warning',
                'message': f"System at {avg_utilization:.1f}% utilization, {avg_coverage:.1f}% coverage",
                'recommendation': "System operating normally" if avg_coverage > 90 else "Review coverage gaps"
            })
        except Exception as e:
            print(f"Error generating insights: {e}")
            insights.append({
                'type': 'System',
                'severity': 'danger',
                'message': 'Unable to generate insights. Please check data.',
                'recommendation': 'Ensure all required data files are present.'
            })
        
        return insights
    
    def get_recent_insights(self):
        """Get most recent insights (for dashboard)"""
        return self.generate_insights()[:5]
    
    def _clean_value(self, value):
        """Clean NaN, Inf, -Inf values for JSON serialization"""
        if value is None:
            return 0
        if isinstance(value, float):
            if math.isnan(value) or math.isinf(value):
                return 0.0
        if pd.isna(value):
            return 0
        return value
    
    def _safe_int(self, value):
        """Safely convert to int"""
        try:
            val = int(value)
            if pd.isna(val):
                return 0
            return val
        except (ValueError, TypeError):
            return 0
    
    def _load_staff_data(self):
        """Load staff data"""
        try:
            return pd.read_csv(self.data_path / 'sample_staff.csv')
        except Exception as e:
            print(f"Error loading staff data: {e}")
            return pd.DataFrame()
    
    def _load_service_data(self):
        """Load service user data"""
        try:
            df = pd.read_csv(self.data_path / 'service_users.csv')
            print(f"Service data columns: {df.columns.tolist()}")
            return df
        except Exception as e:
            print(f"Error loading service data: {e}")
            return pd.DataFrame()
    
    def _load_schedule(self):
        """Load current schedule"""
        try:
            if self.schedule_file.exists():
                with open(self.schedule_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []