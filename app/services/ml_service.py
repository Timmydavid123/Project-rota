# app/services/ml_service.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import cross_val_score
import joblib
from datetime import datetime
from pathlib import Path

class MLService:
    def __init__(self):
        self.models_path = Path('models')
        self.data_path = Path('data')
        self.availability_model = None
        self.preference_model = None
        self.label_encoders = {}
        self.is_trained = False
        self.feature_columns = ['DayOfWeek', 'Month', 'IsWeekend', 'Employee_Encoded', 'Shift_Encoded']
        
        # Create directories if they don't exist
        self.models_path.mkdir(exist_ok=True)
        self.data_path.mkdir(exist_ok=True)
        
        # Try to load existing models
        self.load_models()
    
    def get_staff_data(self):
        """Load staff data"""
        try:
            df = pd.read_csv(self.data_path / 'sample_staff.csv')
            print(f"Staff columns: {df.columns.tolist()}")
            return df
        except FileNotFoundError:
            return self._create_sample_staff()
    
    def get_service_data(self):
        """Load service user data"""
        try:
            df = pd.read_csv(self.data_path / 'service_users.csv')
            print(f"Service columns: {df.columns.tolist()}")
            return df
        except FileNotFoundError:
            return self._create_sample_services()
    
    def get_historical_data(self):
        """Load historical shift data"""
        try:
            df = pd.read_csv(self.data_path / 'historical_shifts.csv')
            print(f"Historical columns: {df.columns.tolist()}")
            return df
        except FileNotFoundError:
            return self._create_sample_historical()
    
    def train_all_models(self):
        """Train all ML models with historical data"""
        print("🤖 Training ML models...")
        
        historical_df = self.get_historical_data()
        
        if len(historical_df) < 10:
            print("⚠️ Insufficient historical data for training")
            return {'error': 'Insufficient data', 'availability_score': 0, 'preference_score': 0, 'performance_score': 0}
        
        try:
            # Prepare features
            features = self._prepare_features(historical_df)
            
            # Train models
            avail_score = self._train_availability_model(features)
            pref_score = self._train_preference_model(features)
            
            self.is_trained = True
            self._save_models()
            
            print("✅ Models trained successfully!")
            
            return {
                'availability_score': avail_score,
                'preference_score': pref_score,
                'performance_score': 0.0  # No performance data available
            }
            
        except Exception as e:
            print(f"❌ Error training models: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e), 'availability_score': 0, 'preference_score': 0, 'performance_score': 0}
    
    def predict_suitability(self, staff_name, shift_type, date, service_user=None):
        """Predict staff suitability score for a shift"""
        if not self.is_trained:
            return 0.5  # Default score
        
        try:
            date_obj = pd.to_datetime(date)
            
            # Prepare features - MUST MATCH TRAINING FEATURES EXACTLY
            features = {
                'DayOfWeek': date_obj.dayofweek,
                'Month': date_obj.month,
                'IsWeekend': 1 if date_obj.dayofweek >= 5 else 0,
            }
            
            # Encode categorical variables
            if 'Employee' in self.label_encoders:
                try:
                    features['Employee_Encoded'] = self.label_encoders['Employee'].transform([staff_name])[0]
                except:
                    features['Employee_Encoded'] = -1
            else:
                features['Employee_Encoded'] = 0
            
            if 'Shift' in self.label_encoders:
                try:
                    features['Shift_Encoded'] = self.label_encoders['Shift'].transform([shift_type])[0]
                except:
                    features['Shift_Encoded'] = -1
            else:
                features['Shift_Encoded'] = 0
            
            # Create feature dataframe with EXACT SAME columns as training
            X = pd.DataFrame([features])[self.feature_columns].fillna(0)
            
            # Get predictions
            avail_prob = 0.5
            pref_prob = 0.5
            
            if self.availability_model:
                try:
                    avail_prob = self.availability_model.predict_proba(X)[0][1]
                except Exception as e:
                    print(f"Availability prediction error: {e}")
            
            if self.preference_model:
                try:
                    pref_prob = self.preference_model.predict_proba(X)[0][1]
                except Exception as e:
                    print(f"Preference prediction error: {e}")
            
            # Combined score
            score = (avail_prob * 0.6 + pref_prob * 0.4)
            
            return round(score, 3)
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return 0.5
    
    def load_models(self):
        """Load pre-trained models from disk"""
        try:
            avail_path = self.models_path / 'availability_model.pkl'
            pref_path = self.models_path / 'preference_model.pkl'
            encoders_path = self.models_path / 'label_encoders.pkl'
            feature_path = self.models_path / 'feature_columns.pkl'
            
            if avail_path.exists():
                self.availability_model = joblib.load(avail_path)
                print("✅ Loaded availability model")
            
            if pref_path.exists():
                self.preference_model = joblib.load(pref_path)
                print("✅ Loaded preference model")
            
            if encoders_path.exists():
                self.label_encoders = joblib.load(encoders_path)
                print("✅ Loaded label encoders")
            
            if feature_path.exists():
                self.feature_columns = joblib.load(feature_path)
                print(f"✅ Loaded feature columns: {self.feature_columns}")
            
            self.is_trained = self.availability_model is not None and self.preference_model is not None
            return self.is_trained
            
        except Exception as e:
            print(f"Error loading models: {e}")
            return False
    
    def _prepare_features(self, df):
        """Prepare features for ML training"""
        features = df.copy()
        
        # Convert date
        features['Date'] = pd.to_datetime(features['Date'])
        
        # Temporal features
        features['DayOfWeek'] = features['Date'].dt.dayofweek
        features['Month'] = features['Date'].dt.month
        features['IsWeekend'] = (features['DayOfWeek'] >= 5).astype(int)
        
        # Encode categorical variables
        categorical_cols = ['Employee', 'Shift']
        
        for col in categorical_cols:
            if col in features.columns:
                le = LabelEncoder()
                features[col] = features[col].fillna('Unknown')
                features[f'{col}_Encoded'] = le.fit_transform(features[col].astype(str))
                self.label_encoders[col] = le
        
        return features
    
    def _train_availability_model(self, features):
        """Train availability prediction model"""
        X = features[self.feature_columns].fillna(0)
        y = features['Worked']
        
        print(f"Training availability model with features: {self.feature_columns}")
        print(f"Training data shape: {X.shape}")
        
        self.availability_model = RandomForestClassifier(
            n_estimators=100, 
            max_depth=10,
            random_state=42
        )
        self.availability_model.fit(X, y)
        
        # Cross-validation
        cv_scores = cross_val_score(self.availability_model, X, y, cv=min(5, len(X)))
        print(f"Availability CV score: {cv_scores.mean():.3f}")
        
        return cv_scores.mean()
    
    def _train_preference_model(self, features):
        """Train preference prediction model"""
        worked_mask = features['Worked'] == 1
        
        X = features[worked_mask][self.feature_columns].fillna(0)
        y = (features[worked_mask]['Preferred'] == 'Y').astype(int)
        
        print(f"Training preference model with features: {self.feature_columns}")
        print(f"Training data shape: {X.shape}")
        
        if len(X) < 5:
            print("⚠️ Not enough data for preference model")
            return 0.0
        
        self.preference_model = LogisticRegression(random_state=42, max_iter=1000)
        self.preference_model.fit(X, y)
        
        # Cross-validation
        cv_scores = cross_val_score(self.preference_model, X, y, cv=min(5, len(X)))
        print(f"Preference CV score: {cv_scores.mean():.3f}")
        
        return cv_scores.mean()
    
    def _save_models(self):
        """Save trained models to disk"""
        if self.availability_model:
            joblib.dump(self.availability_model, self.models_path / 'availability_model.pkl')
            print("✅ Saved availability model")
        if self.preference_model:
            joblib.dump(self.preference_model, self.models_path / 'preference_model.pkl')
            print("✅ Saved preference model")
        if self.label_encoders:
            joblib.dump(self.label_encoders, self.models_path / 'label_encoders.pkl')
            print("✅ Saved label encoders")
        
        # Save feature columns for reference
        joblib.dump(self.feature_columns, self.models_path / 'feature_columns.pkl')
    
    def _create_sample_staff(self):
        """Create sample staff data"""
        data = {
            'Employee ID': list(range(1, 11)),
            'Employee Name': [f'Staff Member {i}' for i in range(1, 11)],
            'Role': ['Support Worker'] * 5 + ['Senior Support Worker'] * 5,
            'Department': ['Care Team'] * 10,
            'Availability': ['Mon;Tue;Wed;Thu;Fri'] * 10,
            'Shift Preference': ['Flexible'] * 10,
            'Max Hours/Week': [40] * 10,
            'Notes': [''] * 10
        }
        df = pd.DataFrame(data)
        df.to_csv(self.data_path / 'sample_staff.csv', index=False)
        return df
    
    def _create_sample_services(self):
        """Create sample service user data"""
        data = {
            'Service User': [f'Service User {i}' for i in range(1, 6)],
            'Shift': ['09:00-17:00'] * 5,
            'Shift Duration (hrs)': [8] * 5,
            'Support Ratio': [1, 2, 1, 2, 3],
            'Days/Week': [5, 7, 5, 7, 5],
            'Weekly Required Hours': [40, 56, 40, 56, 60],
            'Location': ['Home'] * 5,
            'Calculated Hours': [40, 56, 40, 56, 60]
        }
        df = pd.DataFrame(data)
        df.to_csv(self.data_path / 'service_users.csv', index=False)
        return df
    
    def _create_sample_historical(self):
        """Create sample historical data"""
        dates = pd.date_range(end=datetime.now(), periods=90)
        staff = [f'Staff Member {i}' for i in range(1, 11)]
        shifts = ['Morning', 'Afternoon', 'Evening']
        
        data = []
        for date in dates:
            for _ in range(np.random.randint(5, 12)):
                data.append({
                    'Employee': np.random.choice(staff),
                    'Date': date.strftime('%Y-%m-%d'),
                    'Shift': np.random.choice(shifts),
                    'Worked': 1,
                    'Hours': np.random.choice([6, 7, 8, 9, 10]),
                    'Preferred': np.random.choice(['Y', 'N'], p=[0.7, 0.3])
                })
        
        df = pd.DataFrame(data)
        df.to_csv(self.data_path / 'historical_shifts.csv', index=False)
        return df