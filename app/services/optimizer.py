# app/services/optimizer.py - Proportional workload distribution
from ortools.sat.python import cp_model
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
import traceback

class OptimizerService:
    def __init__(self):
        self.model = None
        self.solver = None
        self.data_path = Path('data')
        self.schedule_file = self.data_path / 'current_schedule.json'
    
    def optimize_allocation(self, start_date, num_days, use_ai=True, ai_weight=0.3):
        """Generate optimized staff allocation with proportional fairness"""
        from app.services.ml_service import MLService
        
        print(f"\n{'='*50}")
        print(f"🎯 Starting Optimization with PROPORTIONAL FAIRNESS")
        print(f"{'='*50}")
        
        # Load data
        ml_service = MLService()
        staff_df = ml_service.get_staff_data()
        service_df = ml_service.get_service_data()
        
        print(f"Staff loaded: {len(staff_df)}")
        print(f"Services loaded: {len(service_df)}")
        
        if len(staff_df) == 0 or len(service_df) == 0:
            return {'success': False, 'error': 'No staff or service data available'}
        
        # Generate dates
        dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') 
                 for i in range(num_days)]
        
        # Create fresh model
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        
        try:
            # Create decision variables
            assignments = self._create_variables(staff_df, service_df, dates)
            
            # Add hard constraints
            self._add_coverage_constraints(assignments, service_df, dates)
            self._add_availability_constraints(assignments, staff_df, dates)
            self._add_workload_constraints(assignments, staff_df, service_df, dates)
            self._add_no_overlap_constraints(assignments, staff_df, service_df, dates)
            
            # Build staff capacity dictionary
            staff_capacity = {}
            for _, staff in staff_df.iterrows():
                staff_name = staff['Employee Name']
                max_hours = int(staff.get('Max Hours/Week', 40))
                staff_capacity[staff_name] = max_hours
            
            total_capacity = sum(staff_capacity.values())
            
            # Calculate total required hours
            total_required_hours = 0
            for _, service in service_df.iterrows():
                days_per_week = int(service['Days/Week'])
                hours_per_shift = int(service['Shift Duration (hrs)'])
                support_ratio = int(service['Support Ratio'])
                total_required_hours += days_per_week * hours_per_shift * support_ratio
            
            print(f"Total capacity: {total_capacity} hours")
            print(f"Total required: {total_required_hours} hours")
            print(f"Capacity utilization: {(total_required_hours/total_capacity)*100:.1f}%")
            
            # Calculate TARGET hours for each staff (proportional to their max hours)
            staff_targets = {}
            for staff_name, max_hours in staff_capacity.items():
                # Target = their proportional share of required hours
                proportion = max_hours / total_capacity
                target = total_required_hours * proportion
                staff_targets[staff_name] = min(target, max_hours)  # Cap at max hours
                print(f"  {staff_name}: target={staff_targets[staff_name]:.1f}h (max={max_hours}h)")
            
            # Create variables for actual assigned hours
            staff_hours = {}
            for _, staff in staff_df.iterrows():
                staff_name = staff['Employee Name']
                max_hours = staff_capacity[staff_name]
                hours_var = self.model.NewIntVar(0, max_hours, f"hours_{staff_name}")
                staff_hours[staff_name] = hours_var
                
                # Calculate total hours for this staff
                total_hours = []
                for date in dates:
                    for _, service in service_df.iterrows():
                        service_name = service['Service User']
                        hours = int(service['Shift Duration (hrs)'])
                        var = assignments[date][service_name][staff_name]
                        total_hours.append(var * hours)
                
                self.model.Add(hours_var == sum(total_hours))
            
            # Create deviation variables from target
            over_target = {}
            under_target = {}
            for staff_name, target in staff_targets.items():
                over_target[staff_name] = self.model.NewIntVar(0, 168, f"over_{staff_name}")
                under_target[staff_name] = self.model.NewIntVar(0, int(target), f"under_{staff_name}")
                
                self.model.Add(staff_hours[staff_name] - int(target) == 
                              over_target[staff_name] - under_target[staff_name])
            
            # OBJECTIVE: Maximize assignments while minimizing deviation from targets
            objective_terms = []
            
            # 1. Base value for making assignments (ensures coverage)
            for date in dates:
                for _, service in service_df.iterrows():
                    service_name = service['Service User']
                    for _, staff in staff_df.iterrows():
                        staff_name = staff['Employee Name']
                        var = assignments[date][service_name][staff_name]
                        
                        # High base score to ensure all required shifts are covered
                        score = 10000
                        
                        # Add AI bonus if enabled
                        if use_ai and ml_service.is_trained:
                            shift_type = self._extract_shift_type(service['Shift'])
                            ai_score = ml_service.predict_suitability(
                                staff_name, shift_type, date, service_name
                            )
                            score += int(2000 * ai_score * ai_weight)
                        
                        # Add preference bonus
                        pref = staff.get('Shift Preference', 'Flexible')
                        shift_type = self._extract_shift_type(service['Shift'])
                        if pref == shift_type:
                            score += 500
                        elif pref == 'Flexible':
                            score += 250
                        
                        objective_terms.append(var * score)
            
            # 2. HEAVY PENALTY for being under target (ensures everyone gets proportional hours)
            # Staff with higher max hours have higher targets, so they naturally get more hours
            for staff_name, target in staff_targets.items():
                # Penalty weight is higher for staff with larger capacity
                penalty_weight = int(500 * (staff_capacity[staff_name] / 40))  # Scale by capacity
                
                # Heavy penalty for being under target
                objective_terms.append(under_target[staff_name] * -penalty_weight * 3)
                
                # Small penalty for being over target (to prevent hogging)
                objective_terms.append(over_target[staff_name] * -penalty_weight)
            
            # 3. BONUS for utilizing staff near their max (efficiency)
            for staff_name, hours_var in staff_hours.items():
                max_hours = staff_capacity[staff_name]
                if max_hours >= 35:  # Prioritize filling full-time staff
                    objective_terms.append(hours_var * 100)
            
            self.model.Maximize(sum(objective_terms))
            
            # Solve
            print("🔍 Solving with proportional fairness...")
            self.solver.parameters.max_time_in_seconds = 120.0
            status = self.solver.Solve(self.model)
            
            if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
                schedule = self._extract_solution(assignments, staff_df, service_df, dates)
                metrics = self._calculate_metrics(schedule, staff_df, service_df)
                
                # Calculate actual workload distribution
                workload = {}
                utilization_pct = {}
                for staff_name, hours_var in staff_hours.items():
                    assigned = self.solver.Value(hours_var)
                    max_hours = staff_capacity[staff_name]
                    workload[staff_name] = assigned
                    utilization_pct[staff_name] = round((assigned / max_hours) * 100, 1) if max_hours > 0 else 0
                
                metrics['workload_distribution'] = workload
                metrics['utilization_percentages'] = utilization_pct
                metrics['targets'] = {k: round(v, 1) for k, v in staff_targets.items()}
                
                # Print results
                print(f"\n✅ Schedule created!")
                print(f"   Total assignments: {len(schedule)}")
                print(f"\n📊 Workload Distribution:")
                for staff_name in sorted(workload.keys(), key=lambda x: staff_capacity[x], reverse=True):
                    assigned = workload[staff_name]
                    max_hours = staff_capacity[staff_name]
                    target = staff_targets[staff_name]
                    pct = utilization_pct[staff_name]
                    status = "✅" if abs(assigned - target) < 5 else "⚠️" if assigned < target else "📈"
                    print(f"   {status} {staff_name}: {assigned}/{max_hours}h ({pct}%) [target: {target:.1f}h]")
                
                self._save_schedule(schedule)
                
                return {
                    'success': True,
                    'schedule': schedule,
                    'metrics': metrics,
                    'status': 'optimal' if status == cp_model.OPTIMAL else 'feasible'
                }
            else:
                return {'success': False, 'error': 'No feasible solution found'}
                
        except Exception as e:
            print(f"❌ Optimization error: {e}")
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def _create_variables(self, staff_df, service_df, dates):
        assignments = {}
        for date in dates:
            day_assignments = {}
            for _, service in service_df.iterrows():
                service_name = service['Service User']
                service_assignments = {}
                for _, staff in staff_df.iterrows():
                    staff_name = staff['Employee Name']
                    var_name = f"assign_{date}_{service_name}_{staff_name}".replace(' ', '_')
                    service_assignments[staff_name] = self.model.NewBoolVar(var_name)
                day_assignments[service_name] = service_assignments
            assignments[date] = day_assignments
        return assignments
    
    def _add_coverage_constraints(self, assignments, service_df, dates):
        for date in dates:
            day_of_week = datetime.strptime(date, '%Y-%m-%d').weekday()
            for _, service in service_df.iterrows():
                service_name = service['Service User']
                required_ratio = int(service['Support Ratio'])
                days_per_week = int(service['Days/Week'])
                
                if day_of_week < days_per_week:
                    service_vars = list(assignments[date][service_name].values())
                    self.model.Add(sum(service_vars) == required_ratio)
                else:
                    for var in assignments[date][service_name].values():
                        self.model.Add(var == 0)
    
    def _add_availability_constraints(self, assignments, staff_df, dates):
        for date in dates:
            day_name = datetime.strptime(date, '%Y-%m-%d').strftime('%a')
            for _, staff in staff_df.iterrows():
                staff_name = staff['Employee Name']
                availability = str(staff.get('Availability', ''))
                if day_name not in availability:
                    for service_name in assignments[date]:
                        self.model.Add(assignments[date][service_name][staff_name] == 0)
    
    def _add_workload_constraints(self, assignments, staff_df, service_df, dates):
        for _, staff in staff_df.iterrows():
            staff_name = staff['Employee Name']
            max_hours = int(staff.get('Max Hours/Week', 40))
            total_hours = []
            for date in dates:
                for _, service in service_df.iterrows():
                    service_name = service['Service User']
                    hours = int(service['Shift Duration (hrs)'])
                    var = assignments[date][service_name][staff_name]
                    total_hours.append(var * hours)
            self.model.Add(sum(total_hours) <= max_hours)
    
    def _add_no_overlap_constraints(self, assignments, staff_df, service_df, dates):
        for date in dates:
            for _, staff in staff_df.iterrows():
                staff_name = staff['Employee Name']
                staff_vars = []
                for _, service in service_df.iterrows():
                    service_name = service['Service User']
                    staff_vars.append(assignments[date][service_name][staff_name])
                self.model.Add(sum(staff_vars) <= 1)
    
    def _extract_solution(self, assignments, staff_df, service_df, dates):
        schedule = []
        for date in dates:
            for _, service in service_df.iterrows():
                service_name = service['Service User']
                for _, staff in staff_df.iterrows():
                    staff_name = staff['Employee Name']
                    var = assignments[date][service_name][staff_name]
                    if self.solver.Value(var) == 1:
                        schedule.append({
                            'date': date,
                            'service_user': service_name,
                            'staff_assigned': staff_name,
                            'shift': service['Shift'],
                            'hours': int(service['Shift Duration (hrs)']),
                            'support_ratio': int(service['Support Ratio']),
                            'location': service.get('Location', 'N/A')
                        })
        return schedule
    
    def _calculate_metrics(self, schedule, staff_df, service_df):
        if not schedule:
            return {'total_assignments': 0, 'unique_staff_used': 0, 'unique_services': 0, 
                    'total_hours': 0}
        df = pd.DataFrame(schedule)
        return {
            'total_assignments': len(schedule),
            'unique_staff_used': df['staff_assigned'].nunique(),
            'unique_services': df['service_user'].nunique(),
            'total_hours': int(df['hours'].sum())
        }
    
    def _save_schedule(self, schedule):
        self.data_path.mkdir(exist_ok=True)
        with open(self.schedule_file, 'w') as f:
            json.dump(schedule, f, indent=2)
    
    def _extract_shift_type(self, shift_time):
        try:
            hour = int(shift_time.split(':')[0])
            if hour < 12: return 'Morning'
            elif hour < 17: return 'Afternoon'
            else: return 'Evening'
        except:
            return 'Morning'
    
    def get_current_schedule(self, date=None, staff=None):
        try:
            if self.schedule_file.exists():
                with open(self.schedule_file, 'r') as f:
                    schedule = json.load(f)
                if date:
                    schedule = [s for s in schedule if s['date'] == date]
                if staff:
                    schedule = [s for s in schedule if s['staff_assigned'] == staff]
                return schedule
            return []
        except:
            return []