#!/usr/bin/env python3
"""
MySportsFeeds API Explorer - Simple Single Game Tester
Just test API endpoints and save example outputs for a single game
"""

import os
import sys
import json
import time
from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimpleGameAPIExplorer:
    """Test all MySportsFeeds API endpoints for a single game"""
    
    def __init__(self, game_id='20241023-MIL-PHI'):
        self.api_key = os.getenv('MSF_API_KEY')
        self.password = os.getenv('MSF_PASSWORD', 'MYSPORTSFEEDS')
        self.base_url = 'https://api.mysportsfeeds.com/v2.1/pull/nba'
        self.auth = HTTPBasicAuth(self.api_key, self.password)
        
        # Parse game info
        self.game_id = game_id
        parts = game_id.split('-')
        self.date = parts[0]
        self.away_team = parts[1]
        self.home_team = parts[2]
        
        # Determine season
        year = int(self.date[:4])
        month = int(self.date[4:6])
        if month >= 10:
            self.season = f"{year}-{year+1}-regular"
        else:
            self.season = f"{year-1}-{year}-regular"
        
        # Output directory
        self.output_dir = Path(f'api_responses/{self.game_id}')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def make_request(self, url, params=None):
        """Make API request with simple retry"""
        try:
            response = requests.get(url, auth=self.auth, params=params)
            
            if response.status_code == 429:
                print(f"Rate limited. Waiting 20 seconds...")
                time.sleep(20)
                return self.make_request(url, params)
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def test_endpoint(self, name, url, params=None):
        """Test a single endpoint and save response"""
        print(f"\nTesting: {name}")
        print(f"URL: {url}")
        if params:
            print(f"Params: {params}")
        
        data = self.make_request(url, params)
        
        if data:
            # Save response
            filepath = self.output_dir / f"{name}.json"
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Success - saved to {filepath}")
            
            # Show basic info about response
            if isinstance(data, dict):
                print(f"   Keys: {', '.join(list(data.keys())[:5])}")
        else:
            print(f"❌ Failed")
        
        return data
    
    def run_all_tests(self):
        """Test all available endpoints for this game"""
        print(f"\n{'='*50}")
        print(f"Testing API Endpoints for Game: {self.game_id}")
        print(f"Season: {self.season}")
        print(f"Output: {self.output_dir}")
        print(f"{'='*50}")
        
        # All available endpoints for a single game
        endpoints = [
            # Core endpoints (no addon required)
            ('current_season', f"{self.base_url}/current_season.json", None),
            ('game_info', f"{self.base_url}/{self.season}/games/{self.game_id}.json", None),
            ('daily_games', f"{self.base_url}/{self.season}/date/{self.date}/games.json", None),
            
            # Stats addon endpoints
            ('boxscore', f"{self.base_url}/{self.season}/games/{self.game_id}/boxscore.json", None),
            ('lineup', f"{self.base_url}/{self.season}/games/{self.game_id}/lineup.json", None),
            ('playbyplay', f"{self.base_url}/{self.season}/games/{self.game_id}/playbyplay.json", {'limit': 50}),
            
            ('away_team_gamelog', f"{self.base_url}/{self.season}/date/{self.date}/team_gamelogs.json", {'team': self.away_team}),
            ('home_team_gamelog', f"{self.base_url}/{self.season}/date/{self.date}/team_gamelogs.json", {'team': self.home_team}),
            
            ('away_player_gamelogs', f"{self.base_url}/{self.season}/date/{self.date}/player_gamelogs.json", {'team': self.away_team}),
            ('home_player_gamelogs', f"{self.base_url}/{self.season}/date/{self.date}/player_gamelogs.json", {'team': self.home_team}),
            
            ('away_season_stats', f"{self.base_url}/{self.season}/team_stats_totals.json", {'team': self.away_team}),
            ('home_season_stats', f"{self.base_url}/{self.season}/team_stats_totals.json", {'team': self.home_team}),
            
            ('away_player_season_stats', f"{self.base_url}/{self.season}/player_stats_totals.json", {'team': self.away_team}),
            ('home_player_season_stats', f"{self.base_url}/{self.season}/player_stats_totals.json", {'team': self.home_team}),
            
            ('standings', f"{self.base_url}/{self.season}/standings.json", {'date': self.date}),
            
            # Other useful endpoints
            ('injuries', f"{self.base_url}/injuries.json", {'team': f"{self.away_team},{self.home_team}"}),
            ('away_roster', f"{self.base_url}/players.json", {'team': self.away_team, 'rosterstatus': 'assigned-to-roster'}),
            ('home_roster', f"{self.base_url}/players.json", {'team': self.home_team, 'rosterstatus': 'assigned-to-roster'}),
        ]
        
        # Test each endpoint
        for name, url, params in endpoints:
            self.test_endpoint(name, url, params)
            time.sleep(0.5)  # Be nice to the API
        
        print(f"\n{'='*50}")
        print(f"✅ Testing complete!")
        print(f"All responses saved to: {self.output_dir.absolute()}")
        print(f"{'='*50}\n")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test MySportsFeeds API for a single game')
    parser.add_argument('--game-id', type=str, default='20241023-MIL-PHI',
                       help='Game ID format: YYYYMMDD-AWAY-HOME (default: 20241023-MIL-PHI)')
    
    args = parser.parse_args()
    
    explorer = SimpleGameAPIExplorer(args.game_id)
    explorer.run_all_tests()

if __name__ == "__main__":
    main()