#!/usr/bin/env python3
"""
Main API Testing Script
Run this to test MySportsFeeds API endpoints

Usage:
    python test.py              # Interactive mode
    python test.py --quick       # Test all endpoints quickly
    python test.py --help        # Show help
"""

import sys
from pathlib import Path

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from notebooks.test_api_interactive import main

if __name__ == "__main__":
    main()