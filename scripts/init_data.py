#!/usr/bin/env python
# scripts/init_data.py
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.data_generator import ensure_data_exists, ensure_directories

def main():
    print("=" * 50)
    print("📊 Initializing Data")
    print("=" * 50)
    
    # Create directories
    ensure_directories()
    
    # Create data files
    ensure_data_exists()
    
    print("=" * 50)
    print("✅ Initialization complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()