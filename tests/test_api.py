# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_staff():
    """Test get staff endpoint"""
    response = client.get("/api/staff")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_services():
    """Test get services endpoint"""
    response = client.get("/api/services")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_generate_allocation():
    """Test allocation generation"""
    from datetime import datetime, timedelta
    
    request_data = {
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "num_days": 7,
        "use_ai": False,
        "ai_weight": 0.3
    }
    
    response = client.post("/api/allocate", json=request_data)
    assert response.status_code in [200, 400]  # 400 if no feasible solution

def test_get_analytics():
    """Test analytics endpoints"""
    coverage_response = client.get("/api/analytics/coverage")
    assert coverage_response.status_code == 200
    
    utilization_response = client.get("/api/analytics/utilization")
    assert utilization_response.status_code == 200
    
    insights_response = client.get("/api/analytics/insights")
    assert insights_response.status_code == 200

def test_ml_status():
    """Test ML status endpoint"""
    response = client.get("/api/ml/status")
    assert response.status_code == 200
    assert "trained" in response.json()