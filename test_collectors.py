#!/usr/bin/env python3
"""
Test script for matchup report collectors
Run from project root: python test_collectors.py
"""

import json
from datetime import datetime
from src.data.collectors.game_header import GameHeaderCollector

def test_game_header():
    """Test the game header collector"""
    print("="*60)
    print("TESTING GAME HEADER COLLECTOR")
    print("="*60)
    
    # Initialize collector
    collector = GameHeaderCollector()
    
    # Test with MIL @ PHI on Jan 19, 2025 (they should have played once already)
    away_team = 'MIL'
    home_team = 'PHI'
    date = '20250119'  # Changed to January 19, 2025
    
    print(f"\nCollecting data for: {away_team} @ {home_team} on {date}")
    print("-"*40)
    
    # Collect data
    data = collector.collect(away_team, home_team, date)
    
    # Display results in a nice format
    print("\n📊 GAME INFORMATION")
    print("-"*40)
    game = data['game_info']
    print(f"📍 Location: {game['stadium']}")
    print(f"🏙️ City/State: {game['city_state']}")
    print(f"📅 Date: {game['date']}")
    print(f"🕐 Time: {game['time']}")
    
    print("\n🏀 AWAY TEAM: {abbreviation}".format(**data['away_team']))
    print("-"*40)
    away = data['away_team']
    print(f"Team: {away['name']}")
    print(f"Location: {away['city_state']}")
    print(f"Conference: {away['conference']} - {away['division']}")
    print(f"Records:")
    print(f"  Overall: {away['records']['overall']}")
    print(f"  Conference: {away['records']['conference']}")
    print(f"  Division: {away['records']['division']}")
    
    print("\n🏀 HOME TEAM: {abbreviation}".format(**data['home_team']))
    print("-"*40)
    home = data['home_team']
    print(f"Team: {home['name']}")
    print(f"Location: {home['city_state']}")
    print(f"Conference: {home['conference']} - {home['division']}")
    print(f"Records:")
    print(f"  Overall: {home['records']['overall']}")
    print(f"  Conference: {home['records']['conference']}")
    print(f"  Division: {home['records']['division']}")
    
    print("\n🆚 HEAD-TO-HEAD")
    print("-"*40)
    print(f"Season Series: {data['h2h_season_record']}")
    
    # Save to file
    output_file = f"cache/test_game_header_{away_team}_{home_team}_{date}.json"
    print(f"\n💾 Saving complete data to: {output_file}")
    
    from pathlib import Path
    Path("cache").mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print("\n✅ Test complete!")
    return data

if __name__ == "__main__":
    # Run the test
    data = test_game_header()
    
    print("\n" + "="*60)
    print("Next steps:")
    print("1. Check the data structure in the cache/ folder")
    print("2. Verify all fields are populated correctly")
    print("3. Move on to the next collector (Team Rankings)")
    print("="*60)