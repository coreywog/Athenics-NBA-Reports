#!/usr/bin/env python3
"""
Debug script to test rolling stats integration
"""

import sys
from pathlib import Path
import json

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.collectors.game_header import GameHeaderCollector
from src.data.collectors.team_stats import TeamStatsCollector
from src.data.collectors.rolling_stats import RollingStatsCollector
from src.reports.matchup_report_generator import MatchupReportGenerator

def debug_matchup_report(away_team='MIL', home_team='PHI', game_date='20250119'):
    """Debug function to test all collectors and report generation"""
    
    print(f"\n{'='*60}")
    print(f"🔍 DEBUG: Matchup Report Generation")
    print(f"{'='*60}")
    print(f"Away Team: {away_team}")
    print(f"Home Team: {home_team}")
    print(f"Game Date: {game_date}")
    print(f"{'='*60}\n")
    
    # Initialize collectors
    print("📦 Initializing collectors...")
    header_collector = GameHeaderCollector()
    stats_collector = TeamStatsCollector()
    rolling_collector = RollingStatsCollector()
    print("✅ Collectors initialized\n")
    
    # Collect header data
    print("📊 Collecting header data...")
    header_data = header_collector.collect(away_team, home_team, game_date)
    print(f"✅ Header data keys: {list(header_data.keys())}\n")
    
    # Collect team stats
    print("📊 Collecting team stats...")
    stats_data = stats_collector.collect(away_team, home_team, game_date)
    print(f"✅ Stats data keys: {list(stats_data.keys())}\n")
    
    # Collect rolling stats
    print("📊 Collecting rolling stats...")
    rolling_data = rolling_collector.collect(away_team, home_team, game_date)
    print(f"✅ Rolling data keys: {list(rolling_data.keys())}\n")
    
    # Check rolling stats structure
    print("🔍 Checking rolling stats structure:")
    if 'away_rolling_stats' in rolling_data:
        away_rolling = rolling_data['away_rolling_stats']
        print(f"\n  Away Rolling Stats:")
        for period in ['last_3', 'last_7', 'last_12']:
            if period in away_rolling:
                games = away_rolling[period].get('games_included', 0)
                ps = away_rolling[period].get('ps', 0)
                pa = away_rolling[period].get('pa', 0)
                fg_pct = away_rolling[period].get('fg_pct', 0)
                print(f"    {period}: {games} games | {ps:.1f} PPG | {pa:.1f} OPP PPG | {fg_pct:.1f}% FG")
                
                # Check if all required fields exist
                required_fields = ['ps', 'pa', 'fg', 'fga', 'fg_pct', 'three_p', 'three_pa', 
                                 'three_pct', 'two_p', 'two_pa', 'two_pct', 'ft', 'fta', 
                                 'ft_pct', 'orb', 'drb', 'trb', 'ast', 'stl', 'blk', 'tov']
                missing = [f for f in required_fields if f not in away_rolling[period]]
                if missing:
                    print(f"      ⚠️  Missing fields: {missing}")
            else:
                print(f"    ⚠️  {period} not found!")
    else:
        print("  ⚠️  'away_rolling_stats' key not found!")
    
    if 'home_rolling_stats' in rolling_data:
        home_rolling = rolling_data['home_rolling_stats']
        print(f"\n  Home Rolling Stats:")
        for period in ['last_3', 'last_7', 'last_12']:
            if period in home_rolling:
                games = home_rolling[period].get('games_included', 0)
                ps = home_rolling[period].get('ps', 0)
                pa = home_rolling[period].get('pa', 0)
                fg_pct = home_rolling[period].get('fg_pct', 0)
                print(f"    {period}: {games} games | {ps:.1f} PPG | {pa:.1f} OPP PPG | {fg_pct:.1f}% FG")
                
                # Check if all required fields exist
                required_fields = ['ps', 'pa', 'fg', 'fga', 'fg_pct', 'three_p', 'three_pa', 
                                 'three_pct', 'two_p', 'two_pa', 'two_pct', 'ft', 'fta', 
                                 'ft_pct', 'orb', 'drb', 'trb', 'ast', 'stl', 'blk', 'tov']
                missing = [f for f in required_fields if f not in home_rolling[period]]
                if missing:
                    print(f"      ⚠️  Missing fields: {missing}")
            else:
                print(f"    ⚠️  {period} not found!")
    else:
        print("  ⚠️  'home_rolling_stats' key not found!")
    
    # Combine all data
    print(f"\n📦 Combining all data...")
    combined_data = {**header_data, **stats_data, **rolling_data}
    print(f"✅ Combined data keys: {list(combined_data.keys())}")
    
    # Verify rolling stats are in combined data
    print(f"\n🔍 Verifying combined data has rolling stats:")
    print(f"  - 'away_rolling_stats' present: {'away_rolling_stats' in combined_data}")
    print(f"  - 'home_rolling_stats' present: {'home_rolling_stats' in combined_data}")
    
    # Save combined data to debug file
    debug_file = Path('debug_combined_data.json')
    with open(debug_file, 'w') as f:
        # Convert to JSON-serializable format
        def make_serializable(obj):
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            return str(obj)
        
        json.dump(combined_data, f, indent=2, default=make_serializable)
    print(f"\n💾 Debug data saved to: {debug_file.absolute()}")
    
    # Generate report
    print(f"\n📝 Generating HTML report...")
    generator = MatchupReportGenerator()
    report_path = generator.generate_report(combined_data)
    
    print(f"\n{'='*60}")
    print(f"✅ REPORT GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"📂 Report Location: {report_path}")
    print(f"🌐 Open in browser: file://{report_path.absolute()}")
    print(f"📊 Debug data saved: {debug_file.absolute()}")
    print(f"{'='*60}\n")
    
    return report_path, combined_data

if __name__ == "__main__":
    # Run debug with default or command line arguments
    import sys
    
    if len(sys.argv) == 4:
        away = sys.argv[1]
        home = sys.argv[2]
        date = sys.argv[3]
        debug_matchup_report(away, home, date)
    else:
        debug_matchup_report('MIL', 'PHI', '20250119')