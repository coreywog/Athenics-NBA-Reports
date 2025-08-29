#!/usr/bin/env python3
"""
MySportsFeeds API Explorer
Main test runner for all API endpoints
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
import backoff

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

console = Console()

class APIExplorer:
    """Test all MySportsFeeds API endpoints"""
    
    def __init__(self):
        self.api_key = os.getenv('MSF_API_KEY')
        self.password = os.getenv('MSF_PASSWORD', 'MYSPORTSFEEDS')
        self.base_url = 'https://api.mysportsfeeds.com/v2.1/pull/nba'
        self.auth = HTTPBasicAuth(self.api_key, self.password)
        self.session = requests.Session()
        self.session.auth = self.auth
        
        # Create output directory for responses
        self.output_dir = Path('api_responses')
        self.output_dir.mkdir(exist_ok=True)
        
        # Test parameters
        self.season = '2024-2025-regular'
        self.date = '20241023'  # Oct 23, 2024
        self.game = '20241023-MIL-PHI'
        self.team = 'MIL'
        self.player = 'giannis-antetokounmpo'
        
    @backoff.on_exception(
        backoff.expo,
        requests.exceptions.RequestException,
        max_tries=3,
        max_time=30
    )
    def make_request(self, url, params=None):
        """Make API request with retry logic"""
        response = self.session.get(url, params=params)
        
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            console.print(f"[yellow]Rate limited. Waiting {retry_after} seconds...[/yellow]")
            time.sleep(retry_after)
            return self.make_request(url, params)
        
        response.raise_for_status()
        return response
    
    def save_response(self, endpoint_name, response_data):
        """Save API response to file"""
        filepath = self.output_dir / f"{endpoint_name}.json"
        with open(filepath, 'w') as f:
            json.dump(response_data, f, indent=2)
        return filepath
    
    def test_endpoint(self, name, url, params=None, description=""):
        """Test a single endpoint"""
        console.print(f"\n[bold cyan]Testing: {name}[/bold cyan]")
        if description:
            console.print(f"[dim]{description}[/dim]")
        console.print(f"URL: {url}")
        
        try:
            response = self.make_request(url, params)
            data = response.json()
            
            # Save response
            filepath = self.save_response(name, data)
            
            # Display summary
            self.display_response_summary(name, data, filepath)
            
            return True, data
            
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            return False, None
    
    def display_response_summary(self, name, data, filepath):
        """Display summary of API response"""
        # Basic stats
        stats = {
            "Status": "✅ Success",
            "File saved": str(filepath),
            "Response size": f"{len(json.dumps(data))} bytes"
        }
        
        # Analyze structure
        if isinstance(data, dict):
            stats["Top-level keys"] = ", ".join(list(data.keys())[:5])
            if 'references' in data:
                refs = data['references']
                for key in ['teamReferences', 'playerReferences', 'gameReferences']:
                    if key in refs:
                        stats[key] = f"{len(refs[key])} items"
        
        # Create table
        table = Table(title=f"Response Summary: {name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in stats.items():
            table.add_row(key, str(value))
        
        console.print(table)
    
    def run_core_endpoints(self):
        """Test CORE endpoints (no addon required)"""
        console.print(Panel("[bold green]Testing CORE Endpoints[/bold green]"))
        
        endpoints = [
            ("current_season", f"{self.base_url}/current_season.json", None, 
             "Returns current season info"),
            ("latest_updates", f"{self.base_url}/{self.season}/latest_updates.json", None,
             "Lists update timestamps for each feed"),
            ("seasonal_venues", f"{self.base_url}/{self.season}/venues.json", None,
             "Lists all venues for the season"),
            ("daily_games", f"{self.base_url}/{self.season}/date/{self.date}/games.json", None,
             "All games on a given date"),
            ("seasonal_games", f"{self.base_url}/{self.season}/games.json", 
             {"team": self.team, "limit": 5},
             "All games for a season (limited to 5 for testing)"),
        ]
        
        for endpoint in endpoints:
            self.test_endpoint(*endpoint)
            time.sleep(1)  # Be nice to the API
    
    def run_stats_endpoints(self):
        """Test STATS addon endpoints"""
        console.print(Panel("[bold green]Testing STATS Endpoints[/bold green]"))
        
        endpoints = [
            ("seasonal_team_stats", f"{self.base_url}/{self.season}/team_stats_totals.json",
             {"team": self.team},
             "Seasonal team statistics"),
            ("seasonal_player_stats", f"{self.base_url}/{self.season}/player_stats_totals.json",
             {"team": self.team, "limit": 10},
             "Seasonal player statistics"),
            ("daily_team_gamelogs", f"{self.base_url}/{self.season}/date/{self.date}/team_gamelogs.json",
             {"team": self.team},
             "Team game logs for a date"),
            ("daily_player_gamelogs", f"{self.base_url}/{self.season}/date/{self.date}/player_gamelogs.json",
             {"team": self.team, "limit": 5},
             "Player game logs for a date"),
            ("seasonal_standings", f"{self.base_url}/{self.season}/standings.json", None,
             "Current standings with stats"),
        ]
        
        for endpoint in endpoints:
            self.test_endpoint(*endpoint)
            time.sleep(1)
    
    def run_detailed_endpoints(self):
        """Test DETAILED addon endpoints"""
        console.print(Panel("[bold green]Testing DETAILED Endpoints[/bold green]"))
        
        endpoints = [
            ("game_boxscore", f"{self.base_url}/{self.season}/games/{self.game}/boxscore.json", None,
             "Complete boxscore for a game"),
            ("game_lineup", f"{self.base_url}/{self.season}/games/{self.game}/lineup.json", None,
             "Game lineups"),
            ("game_playbyplay", f"{self.base_url}/{self.season}/games/{self.game}/playbyplay.json",
             {"limit": 20},
             "Play-by-play data (limited for testing)"),
            ("players", f"{self.base_url}/players.json",
             {"team": self.team, "limit": 10},
             "Player bios and details"),
            ("injuries", f"{self.base_url}/injuries.json", None,
             "Current injury report"),
            ("injury_history", f"{self.base_url}/injury_history.json",
             {"team": self.team},
             "Injury history for team"),
        ]
        
        for endpoint in endpoints:
            self.test_endpoint(*endpoint)
            time.sleep(1)
    
    def run_all_tests(self):
        """Run all endpoint tests"""
        console.print(Panel.fit(
            "[bold magenta]MySportsFeeds API Explorer[/bold magenta]\n"
            f"Season: {self.season}\n"
            f"Test Date: {self.date}\n"
            f"Test Team: {self.team}",
            title="Configuration"
        ))
        
        # Test connectivity
        console.print("\n[yellow]Testing API connectivity...[/yellow]")
        success, _ = self.test_endpoint(
            "connectivity_test",
            f"{self.base_url}/current_season.json",
            description="Verifying API credentials"
        )
        
        if not success:
            console.print("[red]Failed to connect to API. Check your credentials.[/red]")
            return
        
        # Run test suites
        self.run_core_endpoints()
        self.run_stats_endpoints()
        self.run_detailed_endpoints()
        
        # Summary
        console.print(Panel(
            f"[green]✅ Testing complete![/green]\n"
            f"Response files saved to: {self.output_dir.absolute()}",
            title="Summary"
        ))
    
    def explore_single_endpoint(self, endpoint_name):
        """Explore a single endpoint in detail"""
        # This method can be expanded to test specific endpoints
        pass

def main():
    """Main entry point"""
    explorer = APIExplorer()
    
    if len(sys.argv) > 1:
        # Test specific endpoint
        endpoint = sys.argv[1]
        console.print(f"Testing specific endpoint: {endpoint}")
        # Add logic for specific endpoint testing
    else:
        # Test all endpoints
        explorer.run_all_tests()

if __name__ == "__main__":
    main()