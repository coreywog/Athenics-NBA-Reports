#!/usr/bin/env python3
"""
Interactive MySportsFeeds API Tester
Allows you to test individual endpoints with custom parameters
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import print as rprint
from rich.prompt import Prompt, Confirm

# Load environment variables
load_dotenv()

console = Console()

# Import endpoint configurations
sys.path.insert(0, str(Path(__file__).parent))
from endpoints_config import ENDPOINTS, TEST_DATA, COMMON_STATS

class InteractiveAPITester:
    def __init__(self):
        self.api_key = os.getenv('MSF_API_KEY')
        self.password = os.getenv('MSF_PASSWORD', 'MYSPORTSFEEDS')
        self.base_url = 'https://api.mysportsfeeds.com/v2.1/pull/nba'
        self.auth = HTTPBasicAuth(self.api_key, self.password)
        
        # Create output directory
        self.output_dir = Path('api_responses')
        self.output_dir.mkdir(exist_ok=True)
        
        # Track request count for rate limiting
        self.request_count = 0
        self.last_request_time = None
        
    def make_request(self, url, params=None):
        """Make API request with rate limiting"""
        # Simple rate limiting - wait 1 second between requests
        if self.last_request_time:
            elapsed = time.time() - self.last_request_time
            if elapsed < 1:
                time.sleep(1 - elapsed)
        
        try:
            response = requests.get(url, auth=self.auth, params=params)
            self.last_request_time = time.time()
            self.request_count += 1
            
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                console.print(f"[yellow]Rate limited. Waiting {retry_after} seconds...[/yellow]")
                time.sleep(retry_after)
                return self.make_request(url, params)
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.HTTPError as e:
            console.print(f"[red]HTTP Error: {e}[/red]")
            console.print(f"[red]Response: {e.response.text if e.response else 'No response'}[/red]")
            raise
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise
    
    def select_endpoint_category(self):
        """Let user select endpoint category"""
        console.print(Panel("[bold cyan]Select Endpoint Category[/bold cyan]"))
        
        categories = list(ENDPOINTS.keys())
        for i, cat in enumerate(categories, 1):
            console.print(f"{i}. {cat}")
        
        choice = Prompt.ask("Select category", choices=[str(i) for i in range(1, len(categories)+1)])
        return categories[int(choice)-1]
    
    def select_endpoint(self, category):
        """Let user select specific endpoint"""
        console.print(Panel(f"[bold cyan]Select {category} Endpoint[/bold cyan]"))
        
        endpoints = list(ENDPOINTS[category].keys())
        for i, ep in enumerate(endpoints, 1):
            ep_info = ENDPOINTS[category][ep]
            console.print(f"{i}. [green]{ep}[/green] - {ep_info['description']}")
        
        choice = Prompt.ask("Select endpoint", choices=[str(i) for i in range(1, len(endpoints)+1)])
        return endpoints[int(choice)-1]
    
    def build_url(self, category, endpoint_name):
        """Build URL for endpoint"""
        endpoint = ENDPOINTS[category][endpoint_name]
        path = endpoint['path']
        
        # Replace placeholders
        url = self.base_url + path
        
        # Handle season placeholder
        if '{season}' in url:
            season = Prompt.ask("Enter season", default=TEST_DATA['season'])
            url = url.replace('{season}', season)
        
        # Handle date placeholder
        if '{date}' in url:
            date = Prompt.ask("Enter date (YYYYMMDD)", default=TEST_DATA['date'])
            url = url.replace('{date}', date)
        
        # Handle game placeholder
        if '{game}' in url:
            game = Prompt.ask("Enter game ID (YYYYMMDD-AWAY-HOME)", default=TEST_DATA['game'])
            url = url.replace('{game}', game)
        
        # Add format
        format_type = Prompt.ask("Format", choices=['json', 'xml', 'csv'], default='json')
        url = url + f'.{format_type}'
        
        return url, endpoint
    
    def get_parameters(self, endpoint):
        """Get optional parameters from user"""
        params = {}
        
        if not endpoint.get('params'):
            return params
        
        console.print("\n[yellow]Optional Parameters (press Enter to skip):[/yellow]")
        
        for param, desc in endpoint['params'].items():
            if param == 'force':
                continue  # Skip force parameter for simplicity
            
            # Provide helpful prompts based on parameter type
            if param == 'team':
                value = Prompt.ask(f"{param} (e.g., MIL or MIL,LAL)", default="")
            elif param == 'stats':
                console.print(f"Common stats: {', '.join(COMMON_STATS['team'][:5])}")
                value = Prompt.ask(f"{param} (comma-separated)", default="")
            elif param == 'limit':
                value = Prompt.ask(f"{param} (number)", default="")
            elif param == 'offset':
                value = Prompt.ask(f"{param} (number)", default="")
            else:
                value = Prompt.ask(f"{param}", default="")
            
            if value:
                params[param] = value
        
        return params
    
    def display_response(self, response_data, endpoint_name):
        """Display response in a nice format"""
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{endpoint_name}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(response_data, f, indent=2)
        
        console.print(f"\n[green]✅ Response saved to: {filepath}[/green]")
        
        # Display summary
        console.print(Panel("[bold]Response Structure[/bold]"))
        
        if isinstance(response_data, dict):
            # Show top-level keys
            table = Table(title="Top-level Keys")
            table.add_column("Key", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("Count/Value", style="green")
            
            for key in list(response_data.keys())[:10]:  # Limit to first 10 keys
                value = response_data[key]
                if isinstance(value, list):
                    count = f"{len(value)} items"
                elif isinstance(value, dict):
                    count = f"{len(value)} keys"
                else:
                    count = str(value)[:50]
                
                table.add_row(key, type(value).__name__, count)
            
            console.print(table)
            
            # Show sample data if available
            if 'references' in response_data:
                self.show_references(response_data['references'])
            
            # Show first item if it's a list in a data key
            for key in ['games', 'teams', 'players', 'gamelogs', 'standings']:
                if key in response_data and isinstance(response_data[key], list) and len(response_data[key]) > 0:
                    console.print(f"\n[cyan]Sample {key} item:[/cyan]")
                    sample = json.dumps(response_data[key][0], indent=2)[:500]
                    syntax = Syntax(sample, "json", theme="monokai")
                    console.print(syntax)
                    break
    
    def show_references(self, references):
        """Show reference data summary"""
        console.print("\n[cyan]References Summary:[/cyan]")
        
        for ref_type in ['teamReferences', 'playerReferences', 'gameReferences']:
            if ref_type in references and references[ref_type]:
                count = len(references[ref_type])
                console.print(f"  • {ref_type}: {count} items")
                if count > 0:
                    # Show first item as example
                    first_item = references[ref_type][0] if isinstance(references[ref_type], list) else \
                                 list(references[ref_type].values())[0]
                    console.print(f"    Example: {json.dumps(first_item, indent=4)[:200]}...")
    
    def run_interactive_session(self):
        """Run interactive testing session"""
        console.print(Panel.fit(
            "[bold magenta]MySportsFeeds API Interactive Tester[/bold magenta]\n"
            "Explore and test individual endpoints",
            title="Welcome"
        ))
        
        # Check credentials
        if not self.api_key:
            console.print("[red]Error: MSF_API_KEY not found in environment[/red]")
            return
        
        while True:
            try:
                # Select category
                category = self.select_endpoint_category()
                
                # Select endpoint
                endpoint_name = self.select_endpoint(category)
                
                # Build URL
                url, endpoint = self.build_url(category, endpoint_name)
                
                # Get parameters
                params = self.get_parameters(endpoint)
                
                # Show what we're about to request
                console.print(Panel(
                    f"[bold]Request Details[/bold]\n"
                    f"URL: {url}\n"
                    f"Params: {json.dumps(params, indent=2) if params else 'None'}",
                    title="Sending Request"
                ))
                
                # Make request
                console.print("[yellow]Making request...[/yellow]")
                response = self.make_request(url, params)
                data = response.json()
                
                # Display response
                self.display_response(data, endpoint_name)
                
                # Continue?
                if not Confirm.ask("\nTest another endpoint?"):
                    break
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted by user[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                if not Confirm.ask("Continue testing?"):
                    break
        
        console.print(f"\n[green]Session complete. Total requests: {self.request_count}[/green]")

@click.command()
@click.option('--quick', is_flag=True, help='Run quick test of all endpoints')
@click.option('--endpoint', help='Test specific endpoint by name')
def main(quick, endpoint):
    """MySportsFeeds API Interactive Tester"""
    tester = InteractiveAPITester()
    
    if quick:
        # Import and run the main explorer
        from api_explorer import APIExplorer
        explorer = APIExplorer()
        explorer.run_all_tests()
    elif endpoint:
        # Test specific endpoint (to be implemented)
        console.print(f"Testing endpoint: {endpoint}")
    else:
        # Run interactive session
        tester.run_interactive_session()