#!/usr/bin/env python3
"""
Debug script to see what the standings API actually returns
"""

import os
import json
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

def debug_standings():
    """Check what fields are available in standings response"""
    
    api_key = os.getenv('MSF_API_KEY')
    password = os.getenv('MSF_PASSWORD', 'MYSPORTSFEEDS')
    auth = HTTPBasicAuth(api_key, password)
    
    # Try for 2024-2025 season
    url = "https://api.mysportsfeeds.com/v2.1/pull/nba/2024-2025-regular/standings.json"
    params = {'team': 'MIL,PHI'}
    
    print("Fetching standings for MIL and PHI...")
    print(f"URL: {url}")
    print("-" * 60)
    
    try:
        response = requests.get(url, auth=auth, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Save full response
        with open('cache/debug_standings.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print("Full response saved to cache/debug_standings.json")
        print("\n" + "="*60)
        
        # Examine structure
        if 'teams' in data:
            for team_data in data['teams']:
                team = team_data.get('team', {})
                team_abbr = team.get('abbreviation', '')
                
                print(f"\nTEAM: {team_abbr}")
                print("-" * 40)
                
                stats = team_data.get('stats', {})
                standings = stats.get('standings', {})
                
                print("Available standings fields:")
                for key, value in standings.items():
                    print(f"  {key}: {value}")
                
                print("\nLooking for conference/division records...")
                
                # Check various possible field names
                possible_fields = [
                    'confWins', 'confLosses', 'divWins', 'divLosses',
                    'conferenceWins', 'conferenceLosses', 'divisionWins', 'divisionLosses',
                    'conf_wins', 'conf_losses', 'div_wins', 'div_losses'
                ]
                
                for field in possible_fields:
                    if field in standings:
                        print(f"  ✓ Found: {field} = {standings[field]}")
                
                # Check if there's nested structure
                if 'conferenceStandings' in stats:
                    print("\n  Found conferenceStandings:")
                    pprint(stats['conferenceStandings'])
                
                if 'divisionStandings' in stats:
                    print("\n  Found divisionStandings:")
                    pprint(stats['divisionStandings'])
        
        print("\n" + "="*60)
        print("Check cache/debug_standings.json for complete response")
        
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text[:500]}")

if __name__ == "__main__":
    from pathlib import Path
    Path("cache").mkdir(exist_ok=True)
    debug_standings()