#!/usr/bin/env python3
"""
Runner script for matchup report generator
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.reports.matchup_report_generator import MatchupReportGenerator
from src.data.collectors.game_header import GameHeaderCollector

if __name__ == "__main__":
    # Collect data
    collector = GameHeaderCollector()
    data = collector.collect('MIL', 'PHI', '20250119')
    
    # Generate report
    generator = MatchupReportGenerator()
    report_path = generator.generate_report(data)
    
    print(f"\n✅ Report generated successfully!")
    print(f"Open in browser: file://{report_path.absolute()}")