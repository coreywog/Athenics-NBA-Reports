#!/usr/bin/env python3
"""
Rolling Stats Collector
Calculates team statistics for last 3, 7, and 12 games
"""

import os
import requests
from typing import Dict, List, Optional
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import time
from datetime import datetime

load_dotenv()

class RollingStatsCollector:
    """Collects rolling statistics for teams (last 3, 7, 12 games)"""
    
    def __init__(self):
        self.api_key = os.getenv('MSF_API_KEY')
        self.password = os.getenv('MSF_PASSWORD', 'MYSPORTSFEEDS')
        self.base_url = 'https://api.mysportsfeeds.com/v2.1/pull/nba'
        self.auth = HTTPBasicAuth(self.api_key, self.password)
        
        # Rate limiting - INCREASED DELAYS
        self.request_delay = 5.0  # Increased from 2 to 5 seconds between requests
        self.retry_delay = 30  # Increased from 20 to 30 seconds on rate limit
        self.max_retries = 3  # Maximum number of retries for rate-limited requests
        
        # Abbreviation mappings
        self.common_to_api = {
            'BKN': 'BRO',
            'OKC': 'OKL',
        }
    
    def _convert_to_api_abbr(self, common_abbr: str) -> str:
        """Convert common abbreviation to API abbreviation"""
        return self.common_to_api.get(common_abbr, common_abbr)
    
    def _get_season(self, date: str) -> str:
        """Determine season from date"""
        year = int(date[:4])
        month = int(date[4:6])
        if month >= 10:
            return f"{year}-{year+1}-regular"
        else:
            return f"{year-1}-{year}-regular"
    
    def _make_request(self, endpoint: str, params: Dict = None, retry_count: int = 0) -> Optional[Dict]:
        """Make API request with improved rate limiting and retry logic"""
        url = f"{self.base_url}/{endpoint}"
        
        # Always wait before making a request
        time.sleep(self.request_delay)
        
        try:
            response = requests.get(url, auth=self.auth, params=params)
            
            if response.status_code == 429:
                if retry_count < self.max_retries:
                    wait_time = self.retry_delay * (retry_count + 1)  # Progressive backoff
                    print(f"  ⚠️  Rate limited. Waiting {wait_time} seconds... (Retry {retry_count + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                    return self._make_request(endpoint, params, retry_count + 1)
                else:
                    print(f"  ❌ Max retries reached. Skipping this request.")
                    return None
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return None
    
    def get_team_game_logs(self, team: str, season: str, before_date: str) -> List[Dict]:
        """Get team game logs before a specific date"""
        endpoint = f"{season}/team_gamelogs.json"
        params = {
            'team': team,
            'limit': 12  # Get last 12 games max
        }
        
        data = self._make_request(endpoint, params)
        
        if not data or 'gamelogs' not in data:
            print(f"  ⚠️  No game logs found for {team}")
            return []
        
        # Filter games before the target date and sort by date (most recent first)
        game_logs = []
        for log in data['gamelogs']:
            game = log.get('game', {})
            game_date = game.get('startTime', '')[:10].replace('-', '')  # Convert to YYYYMMDD
            
            if game_date < before_date:
                game_logs.append(log)
        
        # Sort by date descending (most recent first)
        game_logs.sort(key=lambda x: x['game']['startTime'], reverse=True)
        
        print(f"  ✓ Found {len(game_logs[:12])} games for {team}")
        return game_logs[:12]  # Return only the last 12 games
    
    def calculate_averages(self, game_logs: List[Dict], num_games: int) -> Dict:
        """Calculate averages for the specified number of games"""
        
        if not game_logs or len(game_logs) == 0:
            return self._empty_stats()
        
        # Take only the number of games we need
        games_to_avg = game_logs[:min(num_games, len(game_logs))]
        actual_games = len(games_to_avg)
        
        if actual_games == 0:
            return self._empty_stats()
        
        # Initialize totals
        totals = {
            'pts': 0, 'pts_against': 0,
            'fg_made': 0, 'fg_att': 0,
            'fg3_made': 0, 'fg3_att': 0,
            'fg2_made': 0, 'fg2_att': 0,
            'ft_made': 0, 'ft_att': 0,
            'off_reb': 0, 'def_reb': 0, 'reb': 0,
            'ast': 0, 'stl': 0, 'blk': 0, 'tov': 0
        }
        
        # Sum up all stats
        for log in games_to_avg:
            stats = log.get('stats', {})  # This line MUST be here first

            # Points scored
            offense = stats.get('offense', {})
            totals['pts'] += offense.get('pts', 0)
            
            # Points allowed - get from defense stats
            defense = stats.get('defense', {})
            totals['pts_against'] += defense.get('ptsAgainst', 0)
            
            # Field goals (total)
            fg = stats.get('fieldGoals', {})
            totals['fg_made'] += fg.get('fgMade', 0)
            totals['fg_att'] += fg.get('fgAtt', 0)
            
            # 3-pointers
            totals['fg3_made'] += fg.get('fg3PtMade', 0)
            totals['fg3_att'] += fg.get('fg3PtAtt', 0)
            
            # 2-pointers - Check if API provides these directly, otherwise calculate
            if 'fg2PtMade' in fg and 'fg2PtAtt' in fg:
                totals['fg2_made'] += fg.get('fg2PtMade', 0)
                totals['fg2_att'] += fg.get('fg2PtAtt', 0)
            else:
                # Calculate 2-pointers as total FG minus 3-pointers
                fg_made = fg.get('fgMade', 0)
                fg_att = fg.get('fgAtt', 0)
                fg3_made = fg.get('fg3PtMade', 0)
                fg3_att = fg.get('fg3PtAtt', 0)
                totals['fg2_made'] += (fg_made - fg3_made)
                totals['fg2_att'] += (fg_att - fg3_att)
            
            # Free throws
            ft = stats.get('freeThrows', {})
            totals['ft_made'] += ft.get('ftMade', 0)
            totals['ft_att'] += ft.get('ftAtt', 0)
            
            # Rebounds
            reb = stats.get('rebounds', {})
            totals['off_reb'] += reb.get('offReb', 0)
            totals['def_reb'] += reb.get('defReb', 0)
            totals['reb'] += reb.get('reb', 0)
            
            # Assists
            totals['ast'] += offense.get('ast', 0)
            
            # Defensive stats
            defense = stats.get('defense', {})
            totals['stl'] += defense.get('stl', 0)
            totals['blk'] += defense.get('blk', 0)
            totals['tov'] += defense.get('tov', 0)
        
        # Calculate averages for all 21 stats
        stats = {
            'ps': round(totals['pts'] / actual_games, 1),
            'pa': round(totals['pts_against'] / actual_games, 1),
            'fg': round(totals['fg_made'] / actual_games, 1),
            'fga': round(totals['fg_att'] / actual_games, 1),
            'fg_pct': round((totals['fg_made'] / totals['fg_att'] * 100) if totals['fg_att'] > 0 else 0, 1),
            'three_p': round(totals['fg3_made'] / actual_games, 1),
            'three_pa': round(totals['fg3_att'] / actual_games, 1),
            'three_pct': round((totals['fg3_made'] / totals['fg3_att'] * 100) if totals['fg3_att'] > 0 else 0, 1),
            'two_p': round(totals['fg2_made'] / actual_games, 1),
            'two_pa': round(totals['fg2_att'] / actual_games, 1),
            'two_pct': round((totals['fg2_made'] / totals['fg2_att'] * 100) if totals['fg2_att'] > 0 else 0, 1),
            'ft': round(totals['ft_made'] / actual_games, 1),
            'fta': round(totals['ft_att'] / actual_games, 1),
            'ft_pct': round((totals['ft_made'] / totals['ft_att'] * 100) if totals['ft_att'] > 0 else 0, 1),
            'orb': round(totals['off_reb'] / actual_games, 1),
            'drb': round(totals['def_reb'] / actual_games, 1),
            'trb': round(totals['reb'] / actual_games, 1),
            'ast': round(totals['ast'] / actual_games, 1),
            'stl': round(totals['stl'] / actual_games, 1),
            'blk': round(totals['blk'] / actual_games, 1),
            'tov': round(totals['tov'] / actual_games, 1),
            'games_included': actual_games
        }
        
        return stats
    
    def _empty_stats(self) -> Dict:
        """Return empty stats structure"""
        return {
            'ps': 0, 'pa': 0,
            'fg': 0, 'fga': 0, 'fg_pct': 0,
            'three_p': 0, 'three_pa': 0, 'three_pct': 0,
            'two_p': 0, 'two_pa': 0, 'two_pct': 0,
            'ft': 0, 'fta': 0, 'ft_pct': 0,
            'orb': 0, 'drb': 0, 'trb': 0,
            'ast': 0, 'stl': 0, 'blk': 0, 'tov': 0,
            'games_included': 0
        }
    
    def collect(self, away_team: str, home_team: str, date: str) -> Dict:
        """
        Collect rolling statistics for both teams
        
        Args:
            away_team: Away team abbreviation (common format)
            home_team: Home team abbreviation (common format)
            date: Game date in YYYYMMDD format
        
        Returns:
            Dictionary with rolling stats for both teams
        """
        # Convert to API abbreviations
        away_api = self._convert_to_api_abbr(away_team)
        home_api = self._convert_to_api_abbr(home_team)
        
        season = self._get_season(date)
        
        print(f"\n📊 Collecting rolling statistics for {away_team} vs {home_team}")
        print(f"  Season: {season}")
        print(f"  (Calculating last 3, 7, and 12 game averages)")
        print(f"  ⏳ Note: Using 5-second delays between API calls to avoid rate limits")
        
        # Get game logs for away team first
        print(f"\n  • Fetching {away_team} game logs...")
        away_logs = self.get_team_game_logs(away_api, season, date)
        
        # Add extra delay between teams to be safe
        print(f"  ⏳ Waiting before fetching {home_team} data...")
        time.sleep(self.request_delay)
        
        # Get game logs for home team
        print(f"  • Fetching {home_team} game logs...")
        home_logs = self.get_team_game_logs(home_api, season, date)
        
        # Calculate averages for different periods
        print("\n  • Calculating rolling averages...")
        
        # Initialize with empty stats in case of failures
        away_stats = {
            'last_3': self._empty_stats(),
            'last_7': self._empty_stats(),
            'last_12': self._empty_stats()
        }
        
        home_stats = {
            'last_3': self._empty_stats(),
            'last_7': self._empty_stats(),
            'last_12': self._empty_stats()
        }
        
        # Calculate away team stats if we have data
        if away_logs:
            print(f"    - {away_team} averages...")
            away_stats = {
                'last_3': self.calculate_averages(away_logs, 3),
                'last_7': self.calculate_averages(away_logs, 7),
                'last_12': self.calculate_averages(away_logs, 12)
            }
            print(f"      ✓ Last 3: {away_stats['last_3']['games_included']} games")
            print(f"      ✓ Last 7: {away_stats['last_7']['games_included']} games")
            print(f"      ✓ Last 12: {away_stats['last_12']['games_included']} games")
        else:
            print(f"    ⚠️  No data available for {away_team}")
        
        # Calculate home team stats if we have data
        if home_logs:
            print(f"    - {home_team} averages...")
            home_stats = {
                'last_3': self.calculate_averages(home_logs, 3),
                'last_7': self.calculate_averages(home_logs, 7),
                'last_12': self.calculate_averages(home_logs, 12)
            }
            print(f"      ✓ Last 3: {home_stats['last_3']['games_included']} games")
            print(f"      ✓ Last 7: {home_stats['last_7']['games_included']} games")
            print(f"      ✓ Last 12: {home_stats['last_12']['games_included']} games")
        else:
            print(f"    ⚠️  No data available for {home_team}")
        
        print(f"\n  ✅ Rolling statistics collection complete!")
        
        return {
            'away_rolling_stats': away_stats,
            'home_rolling_stats': home_stats
        }


# Test the collector
if __name__ == "__main__":
    collector = RollingStatsCollector()
    
    # Test with a game
    data = collector.collect('LAL', 'BOS', '20250123')
    
    import json
    print("\nRolling Statistics Data:")
    print("=" * 60)
    
    # Show summary of what was collected
    if data.get('away_rolling_stats'):
        away_3 = data['away_rolling_stats']['last_3']
        away_7 = data['away_rolling_stats']['last_7']
        away_12 = data['away_rolling_stats']['last_12']
        print(f"\nLAL Rolling Stats:")
        print(f"  Last 3 games:  {away_3['ps']:.1f} PPG, {away_3['fg_pct']:.1f}% FG")
        print(f"  Last 7 games:  {away_7['ps']:.1f} PPG, {away_7['fg_pct']:.1f}% FG")
        print(f"  Last 12 games: {away_12['ps']:.1f} PPG, {away_12['fg_pct']:.1f}% FG")
    
    if data.get('home_rolling_stats'):
        home_3 = data['home_rolling_stats']['last_3']
        home_7 = data['home_rolling_stats']['last_7']
        home_12 = data['home_rolling_stats']['last_12']
        print(f"\nBOS Rolling Stats:")
        print(f"  Last 3 games:  {home_3['ps']:.1f} PPG, {home_3['fg_pct']:.1f}% FG")
        print(f"  Last 7 games:  {home_7['ps']:.1f} PPG, {home_7['fg_pct']:.1f}% FG")
        print(f"  Last 12 games: {home_12['ps']:.1f} PPG, {home_12['fg_pct']:.1f}% FG")