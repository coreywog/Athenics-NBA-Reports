#!/usr/bin/env python3
"""
Daily Report Runner - Updated with Team Stats and Rolling Stats
Includes team statistics collection, rolling stats, and better rate limiting to avoid 429 errors
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
from src.data.collectors.team_stats import TeamStatsCollector
from src.data.collectors.rolling_stats import RollingStatsCollector  # Added rolling stats
from src.reports.matchup_report_generator import MatchupReportGenerator
from src.data.collectors.team_rankings import TeamRankingsCollector

load_dotenv()

class DailyReportRunner:
    """Generates reports for all NBA games on a specific date"""
    
    def __init__(self):
        self.api_key = os.getenv('MSF_API_KEY')
        self.password = os.getenv('MSF_PASSWORD', 'MYSPORTSFEEDS')
        self.base_url = 'https://api.mysportsfeeds.com/v2.1/pull/nba'
        self.auth = HTTPBasicAuth(self.api_key, self.password)
        
        # Rate limiting settings - increased for rolling stats
        self.request_delay = 3.0  # Increased delay before API calls
        self.retry_delay = 30  # 30 seconds on rate limit
        self.games_delay = 5  # Increased delay between processing games
        
        # API to common abbreviation mapping
        self.api_to_common = {
            'BRO': 'BKN',  # Brooklyn Nets
            'OKL': 'OKC',  # Oklahoma City Thunder
        }
        
        # Initialize collectors and generators
        self.header_collector = GameHeaderCollector()
        self.stats_collector = TeamStatsCollector()
        self.rolling_collector = RollingStatsCollector()  # Added rolling stats collector
        self.report_generator = MatchupReportGenerator()
        self.rankings_collector = TeamRankingsCollector()

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
        """Fetch all games for a specific date with rate limiting"""
        try:
            season = self._get_season(date)
            endpoint = f"{season}/date/{date}/games.json"
            url = f"{self.base_url}/{endpoint}"
            
            print(f"\n📅 Fetching games for {date}...")
            time.sleep(self.request_delay)  # Rate limiting
            
            response = requests.get(url, auth=self.auth)
            
            if response.status_code == 429:
                print(f"  ⚠️  Rate limited. Waiting {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
                response = requests.get(url, auth=self.auth)
            
            response.raise_for_status()
            data = response.json()
            
            games = []
            if data and 'games' in data:
                for game in data['games']:
                    schedule = game.get('schedule', {})
                    score = game.get('score', {})
                    
                    away_team = schedule.get('awayTeam', {}).get('abbreviation')
                    home_team = schedule.get('homeTeam', {}).get('abbreviation')
                    
                    if away_team and home_team:
                        # Convert to common abbreviations
                        away_common = self._convert_to_common_abbr(away_team)
                        home_common = self._convert_to_common_abbr(home_team)
                        
                        # Determine game status
                        played_status = schedule.get('playedStatus', 'UNPLAYED')
                        
                        game_info = {
                            'away_team': away_common,
                            'home_team': home_common,
                            'status': played_status,
                            'game_id': schedule.get('id'),
                            'start_time': schedule.get('startTime')
                        }
                        games.append(game_info)
            
            print(f"  Found {len(games)} games")
            return games
            
        except Exception as e:
            print(f"  ❌ Error fetching games: {e}")
            return []
    
    def generate_report_for_game(self, away_team: str, home_team: str, date: str, 
                                output_dir: Path) -> bool:
        """
        Generate a report for a single game with all collectors including rolling stats
        
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"\n🏀 Generating report for {away_team} @ {home_team}...")
            
            # Collect header data
            print("  📋 Collecting game header data...")
            header_data = self.header_collector.collect(away_team, home_team, date)
            
            # Collect team statistics
            print("  📊 Collecting team statistics...")
            stats_data = self.stats_collector.collect(away_team, home_team, date)
            
            # Collect rolling statistics (last 3, 7, 12 games)
            print("  📈 Collecting rolling statistics...")
            print("     ⏳ This may take a moment due to rate limiting...")
            rolling_data = self.rolling_collector.collect(away_team, home_team, date)
            
            # Collect ranking statistics
            print("  📈 Collecting team rankings...")
            rankings_data = self.rankings_collector.collect(away_team, home_team, date)

            # Combine all collected data
            combined_data = {**header_data, **stats_data, **rolling_data, **rankings_data}
            
            # Generate the report
            output_filename = f"{away_team}_at_{home_team}_{date}.html"
            output_path = output_dir / output_filename
            
            # Save report to the date-specific directory
            self.report_generator.output_dir = output_dir
            self.report_generator.generate_report(combined_data, output_filename)
            
            # Fix the logo paths in the generated HTML file
            self._fix_logo_paths(output_path)
            
            self.processed_games.append({
                'matchup': f"{away_team} @ {home_team}",
                'file': str(output_path)
            })
            
            print(f"  ✅ Report generated: {output_path.name}")
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to generate report: {e}")
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
            print(f"    ⚠️  Could not fix logo paths: {e}")
    
    def run_daily_reports(self, date: str = None, include_unplayed: bool = True) -> Dict:
        """
        Generate reports for all games on a specific date with rate limiting
        
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
        print(f"🏀 NBA Daily Report Generator")
        print(f"📅 Date: {formatted_date}")
        print(f"⏱️  Rate limiting: {self.request_delay}s between API calls")
        print(f"📊 Including: Header, Team Stats, and Rolling Stats")
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
            print("\n❌ No games found for this date.")
            return {
                'date': formatted_date,
                'date_code': date,
                'total_games': 0,
                'processed': 0,
                'failed': 0
            }
        
        # Estimate total time
        est_time_per_game = 30  # seconds (conservative estimate with rolling stats)
        total_est_time = len(games) * est_time_per_game / 60
        print(f"\n⏰ Estimated time: ~{total_est_time:.1f} minutes for {len(games)} games")
        print(f"   (Rolling stats require multiple API calls per team)")
        
        # Process each game with rate limiting
        for i, game in enumerate(games, 1):
            # Skip unplayed games if requested
            if not include_unplayed and game['status'] != 'COMPLETED':
                print(f"\n⏭️  Skipping unplayed game: {game['away_team']} @ {game['home_team']}")
                continue
            
            print(f"\n[{i}/{len(games)}] Processing game...")
            
            # Generate the report
            self.generate_report_for_game(
                game['away_team'],
                game['home_team'],
                date,
                date_output_dir
            )
            
            # Rate limiting between games
            if i < len(games):
                print(f"\n⏳ Waiting {self.games_delay} seconds before next game...")
                time.sleep(self.games_delay)
        
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
        print(f"📊 SUMMARY - {formatted_date}")
        print(f"{'='*60}")
        print(f"Total Games: {summary['total_games']}")
        print(f"✅ Successfully Processed: {summary['processed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"📂 Output Directory: {output_dir}")
        
        if self.failed_games:
            print(f"\n⚠️  Failed Games:")
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
            background: #333;
            border-radius: 5px;
            margin-bottom: 10px;
        }}
        .game-item:hover {{
            background: #444;
        }}
        .game-matchup {{
            font-size: 16px;
            font-weight: 500;
        }}
        .game-link {{
            color: #4CAF50;
            text-decoration: none;
            font-weight: 500;
        }}
        .game-link:hover {{
            text-decoration: underline;
        }}
        .no-games {{
            text-align: center;
            padding: 40px;
            color: #666;
        }}
        .info-note {{
            background: #333;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            font-size: 14px;
            color: #aaa;
        }}
    </style>
</head>
<body>
    <h1>NBA Daily Reports - {summary['date']}</h1>
    
    <div class="summary">
        <div class="summary-stats">
            <div class="stat">
                <div class="stat-value">{summary['total_games']}</div>
                <div class="stat-label">Total Games</div>
            </div>
            <div class="stat">
                <div class="stat-value">{summary['processed']}</div>
                <div class="stat-label">Generated</div>
            </div>
            <div class="stat">
                <div class="stat-value">{summary['failed']}</div>
                <div class="stat-label">Failed</div>
            </div>
        </div>
    </div>
    
    <div class="games-list">
        <h2>Game Reports</h2>
'''
        
        if self.processed_games:
            for game in self.processed_games:
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
        <div class="info-note">
            📊 Reports include: Game header info, season team statistics, and rolling stats (last 3, 7, and 12 games)
        </div>
    </div>
</body>
</html>
'''
        
        # Save index file
        index_path = output_dir / 'index.html'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        print(f"\n📄 Index page created: {index_path}")
    
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
    print(f"📂 View all reports at: output/daily_reports/{summary['date_code']}/index.html")