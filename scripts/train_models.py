#!/usr/bin/env python
# scripts/train_models.py
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.ml_service import MLService
from app.utils.data_generator import ensure_data_exists

def main():
    print("=" * 50)
    print("🤖 Training ML Models")
    print("=" * 50)
    
    # Ensure data exists
    ensure_data_exists()
    
    # Train models
    ml_service = MLService()
    
    if ml_service.is_trained:
        print("✅ Models already trained!")
        return
    
    print("🔄 Training new models...")
    results = ml_service.train_all_models()
    
    if 'error' in results:
        print(f"❌ Training failed: {results['error']}")
        return
    
    print("✅ Training complete!")
    print(f"   Availability Model Score: {results.get('availability_score', 0):.3f}")
    print(f"   Preference Model Score: {results.get('preference_score', 0):.3f}")
    
    # Only print performance score if it exists and is not the placeholder
    perf_score = results.get('performance_score', 0)
    if perf_score > 0:
        print(f"   Performance Model Score: {perf_score:.3f}")
    else:
        print(f"   Performance Model: Not trained (no performance data)")
    
    print("=" * 50)

if __name__ == "__main__":
    main()