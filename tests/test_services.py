# tests/test_services.py
import pytest
import pandas as pd
from app.services.ml_service import MLService
from app.services.optimizer import OptimizerService
from app.services.analytics import AnalyticsService

def test_ml_service_init():
    """Test ML service initialization"""
    service = MLService()
    assert service is not None
    
    # Test data loading
    staff_df = service.get_staff_data()
    assert isinstance(staff_df, pd.DataFrame)
    assert len(staff_df) > 0
    
    service_df = service.get_service_data()
    assert isinstance(service_df, pd.DataFrame)
    assert len(service_df) > 0

def test_optimizer_service():
    """Test optimizer service"""
    service = OptimizerService()
    assert service is not None
    
    # Test schedule loading
    schedule = service.get_current_schedule()
    assert isinstance(schedule, list)

def test_analytics_service():
    """Test analytics service"""
    service = AnalyticsService()
    assert service is not None
    
    # Test stats
    stats = service.get_system_stats()
    assert isinstance(stats, dict)
    assert 'total_staff' in stats
    assert 'total_services' in stats
    
    # Test coverage analysis
    coverage = service.analyze_coverage()
    assert isinstance(coverage, list)
    
    # Test utilization analysis
    utilization = service.analyze_utilization()
    assert isinstance(utilization, list)