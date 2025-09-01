#!/usr/bin/env python3
"""
Test to find the correct season identifier for current NBA season
"""

import os
import json
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def test_seasons():
    """Test different season identifiers to find current data"""
    
    api_key = os.getenv('MSF_API_KEY')
    password = os.getenv('MSF_PASSWORD', 'MYSPORTSFEEDS')
    auth = HTTPBasicAuth(api_key, password)
    base_url = 'https://api.mysportsfeeds.com/v2.1/pull/nba'
    
    print("Testing Season Identifiers")
    print("="*60)
    
    # First, check what the current_season endpoint says
    print("\n1. Checking current_season endpoint...")
    print("-"*40)
    
    try:
        url = f"{base_url}/current_season.json"
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        data = response.json()
        
        print(f"Current Season Response:")
        print(json.dumps(data, indent=2))
        
        # Save for reference
        with open('cache/current_season.json', 'w') as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test different season formats
    print("\n2. Testing different season identifiers...")
    print("-"*40)
    
    season_formats = [
        '2024-2025-regular',     # What we've been using
        '2025-2026-regular',     # Maybe they use the ending year?
        '2024-25-regular',       # Shorter format
        '2025-regular',          # Just the year
        'current',               # Maybe there's a special identifier
        'latest'                 # Another possibility
    ]
    
    for season in season_formats:
        print(f"\nTesting: {season}")
        
        try:
            # Try to get standings for PHI
            url = f"{base_url}/{season}/standings.json"
            params = {'team': 'PHI'}
            
            response = requests.get(url, auth=auth, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check PHI's record
                if 'teams' in data:
                    for team in data['teams']:
                        if team.get('team', {}).get('abbreviation') == 'PHI':
                            standings = team.get('stats', {}).get('standings', {})
                            wins = standings.get('wins', 0)
                            losses = standings.get('losses', 0)
                            
                            print(f"  ✓ SUCCESS - PHI Record: {wins}-{losses}")
                            
                            # Check if this looks like current season (PHI should have fewer than 82 games)
                            total_games = wins + losses
                            if total_games < 82 and total_games > 0:
                                print(f"  👍 This looks like current season data! ({total_games} games played)")
                            elif total_games == 82:
                                print(f"  ⚠️  This looks like a completed season (82 games)")
                            break
            else:
                print(f"  ✗ Failed with status: {response.status_code}")
                
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:50]}")
    
    # Test if we can get a recent game
    print("\n3. Testing for recent games...")
    print("-"*40)
    
    # Try to get games for a recent date
    test_date = '20241225'  # Christmas Day 2024
    
    for season in ['2024-2025-regular', '2025-2026-regular']:
        print(f"\nTrying {season} for date {test_date}...")
        
        try:
            url = f"{base_url}/{season}/date/{test_date}/games.json"
            response = requests.get(url, auth=auth)
            
            if response.status_code == 200:
                data = response.json()
                games = data.get('games', [])
                
                print(f"  Found {len(games)} games on this date")
                
                if games:
                    # Show first game as example
                    game = games[0]
                    schedule = game.get('schedule', {})
                    away = schedule.get('awayTeam', {}).get('abbreviation')
                    home = schedule.get('homeTeam', {}).get('abbreviation')
                    print(f"  Example: {away} @ {home}")
                    
        except Exception as e:
            print(f"  Error: {str(e)[:50]}")
    
    print("\n" + "="*60)
    print("CONCLUSION:")
    print("Check the results above to identify which season format returns current data.")
    print("Look for PHI having fewer than 82 games played.")

if __name__ == "__main__":
    from pathlib import Path
    Path("cache").mkdir(exist_ok=True)
    test_seasons()