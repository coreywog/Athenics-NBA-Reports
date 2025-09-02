#!/usr/bin/env python3
"""
Daily Report Runner
Automatically generates reports for all NBA games on a given date
"""

import os
import sys
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.collectors.game_header import GameHeaderCollector
from src.reports.matchup_report_generator import MatchupReportGenerator

load_dotenv()

class DailyReportRunner:
    """Generates reports for all NBA games on a specific date"""
    
    def __init__(self):
        self.api_key = os.getenv('MSF_API_KEY')
        self.password = os.getenv('MSF_PASSWORD', 'MYSPORTSFEEDS')
        self.base_url = 'https://api.mysportsfeeds.com/v2.1/pull/nba'
        self.auth = HTTPBasicAuth(self.api_key, self.password)
        
        # API to common abbreviation mapping
        self.api_to_common = {
            'BRO': 'BKN',  # Brooklyn Nets
            'OKL': 'OKC',  # Oklahoma City Thunder
        }
        
        # Initialize collectors and generators
        self.header_collector = GameHeaderCollector()
        self.report_generator = MatchupReportGenerator()
        
        # Create output directories
        self.base_output_dir = Path('output/daily_reports')
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Track processing
        self.processed_games = []
        self.failed_games = []
    
    def _convert_to_common_abbr(self, api_abbr: str) -> str:
        """Convert API abbreviation to common abbreviation"""
        return self.api_to_common.get(api_abbr, api_abbr)
    
    def _get_season(self, date: str) -> str:
        """Determine season from date"""
        year = int(date[:4])
        month = int(date[4:6])
        if month >= 10:
            return f"{year}-{year+1}-regular"
        else:
            return f"{year-1}-{year}-regular"
    
    def get_games_for_date(self, date: str) -> List[Dict]:
        """
        Fetch all games scheduled for a specific date
        
        Args:
            date: Date in YYYYMMDD format
            
        Returns:
            List of game dictionaries with team information
        """
        season = self._get_season(date)
        endpoint = f"{self.base_url}/{season}/date/{date}/games.json"
        
        print(f"Fetching games for {date}...")
        
        try:
            time.sleep(0.5)  # Rate limiting
            response = requests.get(endpoint, auth=self.auth)
            response.raise_for_status()
            data = response.json()
            
            games = []
            if data and 'games' in data:
                for game in data['games']:
                    schedule = game.get('schedule', {})
                    
                    # Get API abbreviations
                    away_api = schedule.get('awayTeam', {}).get('abbreviation')
                    home_api = schedule.get('homeTeam', {}).get('abbreviation')
                    
                    # Convert to common abbreviations for display
                    away_common = self._convert_to_common_abbr(away_api)
                    home_common = self._convert_to_common_abbr(home_api)
                    
                    # Extract game information
                    game_info = {
                        'id': schedule.get('id'),
                        'away_team': away_common,  # Use common abbreviation
                        'home_team': home_common,  # Use common abbreviation
                        'away_team_api': away_api,  # Keep API abbreviation for API calls
                        'home_team_api': home_api,  # Keep API abbreviation for API calls
                        'start_time': schedule.get('startTime'),
                        'venue': schedule.get('venue', {}).get('name'),
                        'status': schedule.get('playedStatus', 'UNPLAYED')
                    }
                    
                    # Only include games with valid team data
                    if game_info['away_team'] and game_info['home_team']:
                        games.append(game_info)
            
            print(f"Found {len(games)} games on {date}")
            return games
            
        except Exception as e:
            print(f"Error fetching games for {date}: {e}")
            return []
    
    def generate_report_for_game(self, away_team: str, home_team: str, date: str, 
                                output_dir: Path) -> bool:
        """
        Generate a report for a single game
        
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"\nGenerating report for {away_team} @ {home_team}...")
            
            # Collect data using the header collector
            # (In the future, you'll add other collectors here)
            header_data = self.header_collector.collect(away_team, home_team, date)
            
            # For now, we'll use just the header data
            # In the future, you'll combine data from multiple collectors
            combined_data = header_data
            
            # Generate the report
            output_filename = f"{away_team}_at_{home_team}_{date}.html"
            output_path = output_dir / output_filename
            
            # Save report to the date-specific directory
            self.report_generator.output_dir = output_dir
            
            # Temporarily override the logo paths in the data
            # The report generator will override them to ../../assets/teams/
            # but we need ../../../assets/teams/ for daily reports
            # So we'll fix them after generation by modifying the HTML directly
            self.report_generator.generate_report(combined_data, output_filename)
            
            # Fix the logo paths in the generated HTML file
            self._fix_logo_paths(output_path)
            
            self.processed_games.append({
                'matchup': f"{away_team} @ {home_team}",
                'file': str(output_path)
            })
            
            print(f"✓ Report generated: {output_path.name}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to generate report for {away_team} @ {home_team}: {e}")
            self.failed_games.append({
                'matchup': f"{away_team} @ {home_team}",
                'error': str(e)
            })
            return False
    
    def _fix_logo_paths(self, html_path: Path):
        """Fix logo paths in the generated HTML to work with daily report structure"""
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace ../../assets/teams/ with ../../../assets/teams/
            content = content.replace('../../assets/teams/', '../../../assets/teams/')
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"Warning: Could not fix logo paths: {e}")
    
    def run_daily_reports(self, date: str = None, include_unplayed: bool = True) -> Dict:
        """
        Generate reports for all games on a specific date
        
        Args:
            date: Date in YYYYMMDD format (defaults to today)
            include_unplayed: Whether to generate reports for games not yet played
            
        Returns:
            Summary dictionary with processing results
        """
        # Use today's date if not specified
        if date is None:
            date = datetime.now().strftime('%Y%m%d')
        
        # Format date for display
        date_obj = datetime.strptime(date, '%Y%m%d')
        formatted_date = date_obj.strftime('%B %d, %Y')
        
        print(f"\n{'='*60}")
        print(f"NBA Daily Report Generator")
        print(f"Date: {formatted_date}")
        print(f"{'='*60}")
        
        # Create date-specific output directory
        date_output_dir = self.base_output_dir / date
        date_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Reset tracking
        self.processed_games = []
        self.failed_games = []
        
        # Get all games for the date
        games = self.get_games_for_date(date)
        
        if not games:
            print("\nNo games found for this date.")
            return {
                'date': formatted_date,
                'total_games': 0,
                'processed': 0,
                'failed': 0
            }
        
        # Process each game
        for i, game in enumerate(games, 1):
            # Skip unplayed games if requested
            if not include_unplayed and game['status'] == 'UNPLAYED':
                print(f"\nSkipping unplayed game: {game['away_team']} @ {game['home_team']}")
                continue
            
            print(f"\n[{i}/{len(games)}] Processing {game['away_team']} @ {game['home_team']}...")
            
            # Generate the report using common abbreviations
            # The collector will handle the conversion to API format internally
            self.generate_report_for_game(
                game['away_team'],  # Common abbreviation
                game['home_team'],  # Common abbreviation
                date,
                date_output_dir
            )
            
            # Rate limiting between games
            if i < len(games):
                time.sleep(1)
        
        # Generate summary
        summary = self.generate_summary(date, formatted_date, date_output_dir)
        
        return summary
    
    def generate_summary(self, date: str, formatted_date: str, 
                        output_dir: Path) -> Dict:
        """Generate and save a summary of the daily report generation"""
        
        summary = {
            'date': formatted_date,
            'date_code': date,
            'total_games': len(self.processed_games) + len(self.failed_games),
            'processed': len(self.processed_games),
            'failed': len(self.failed_games),
            'output_directory': str(output_dir),
            'processed_games': self.processed_games,
            'failed_games': self.failed_games
        }
        
        # Print summary to console
        print(f"\n{'='*60}")
        print(f"SUMMARY - {formatted_date}")
        print(f"{'='*60}")
        print(f"Total Games: {summary['total_games']}")
        print(f"Successfully Processed: {summary['processed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Output Directory: {output_dir}")
        
        if self.failed_games:
            print(f"\nFailed Games:")
            for game in self.failed_games:
                print(f"  - {game['matchup']}: {game['error']}")
        
        # Save summary as HTML index
        self.generate_index_page(summary, output_dir)
        
        return summary
    
    def generate_index_page(self, summary: Dict, output_dir: Path):
        """Generate an index HTML page for all reports of the day"""
        
        index_html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NBA Reports - {summary['date']}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a1a;
            color: #fff;
            padding: 20px;
            max-width: 1000px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            color: #fff;
            margin-bottom: 30px;
        }}
        .summary {{
            background: #2a2a2a;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .summary-stats {{
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 15px;
        }}
        .stat {{
            display: flex;
            flex-direction: column;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
        }}
        .stat-label {{
            font-size: 12px;
            color: #999;
            text-transform: uppercase;
            margin-top: 5px;
        }}
        .games-list {{
            background: #2a2a2a;
            padding: 20px;
            border-radius: 10px;
        }}
        .game-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: rgba(255,255,255,0.05);
            border-radius: 5px;
            margin-bottom: 10px;
            transition: background 0.2s;
        }}
        .game-item:hover {{
            background: rgba(255,255,255,0.1);
        }}
        .game-matchup {{
            font-size: 16px;
            font-weight: bold;
        }}
        .game-link {{
            color: #4CAF50;
            text-decoration: none;
            padding: 8px 16px;
            background: rgba(76, 175, 80, 0.2);
            border-radius: 5px;
            transition: background 0.2s;
        }}
        .game-link:hover {{
            background: rgba(76, 175, 80, 0.3);
        }}
        .failed {{
            color: #f44336;
        }}
        .no-games {{
            text-align: center;
            color: #666;
            padding: 40px;
        }}
    </style>
</head>
<body>
    <h1>NBA Daily Reports</h1>
    <h2 style="text-align: center; color: #999;">{summary['date']}</h2>
    
    <div class="summary">
        <div class="summary-stats">
            <div class="stat">
                <div class="stat-value">{summary['total_games']}</div>
                <div class="stat-label">Total Games</div>
            </div>
            <div class="stat">
                <div class="stat-value">{summary['processed']}</div>
                <div class="stat-label">Reports Generated</div>
            </div>
            <div class="stat">
                <div class="stat-value failed">{summary['failed']}</div>
                <div class="stat-label">Failed</div>
            </div>
        </div>
    </div>
    
    <div class="games-list">
        <h3>Game Reports</h3>
'''
        
        if summary['processed_games']:
            for game in summary['processed_games']:
                filename = Path(game['file']).name
                index_html += f'''
        <div class="game-item">
            <span class="game-matchup">{game['matchup']}</span>
            <a href="{filename}" class="game-link">View Report →</a>
        </div>
'''
        else:
            index_html += '''
        <div class="no-games">No reports generated</div>
'''
        
        index_html += '''
    </div>
</body>
</html>
'''
        
        # Save index file
        index_path = output_dir / 'index.html'
        with open(index_path, 'w') as f:
            f.write(index_html)
        
        print(f"\n✓ Index page created: {index_path}")
    
    def run_for_yesterday(self) -> Dict:
        """Convenience method to run reports for yesterday's games"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        return self.run_daily_reports(yesterday, include_unplayed=False)
    
    def run_for_today(self) -> Dict:
        """Convenience method to run reports for today's games"""
        today = datetime.now().strftime('%Y%m%d')
        return self.run_daily_reports(today, include_unplayed=True)


# CLI interface for running reports
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate NBA reports for all games on a date')
    parser.add_argument('--date', type=str, help='Date in YYYYMMDD format (default: today)')
    parser.add_argument('--yesterday', action='store_true', help='Generate reports for yesterday')
    parser.add_argument('--exclude-unplayed', action='store_true', 
                       help='Skip games that haven\'t been played yet')
    
    args = parser.parse_args()
    
    runner = DailyReportRunner()
    
    if args.yesterday:
        summary = runner.run_for_yesterday()
    elif args.date:
        summary = runner.run_daily_reports(args.date, not args.exclude_unplayed)
    else:
        summary = runner.run_for_today()
    
    print(f"\n✅ Daily report generation complete!")
    print(f"View all reports at: output/daily_reports/{summary['date_code']}/index.html")