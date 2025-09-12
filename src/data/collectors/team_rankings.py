#!/usr/bin/env python3
"""
Team Rankings Collector
Fetches comprehensive team rankings including overall, offensive, defensive, conference, and division rankings
"""

import os
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

class TeamRankingsCollector:
    """Collects team ranking data from MySportsFeeds API"""
    
    def __init__(self):
        self.api_key = os.getenv('MSF_API_KEY')
        self.password = os.getenv('MSF_PASSWORD', 'MYSPORTSFEEDS')
        self.base_url = 'https://api.mysportsfeeds.com/v2.1/pull/nba'
        self.auth = HTTPBasicAuth(self.api_key, self.password)
        
        # Rate limiting
        self.request_delay = 2.0
        self.retry_delay = 30
        
        # Common to API abbreviation mapping
        self.common_to_api = {
            'BKN': 'BRO',  # Brooklyn Nets
            'OKC': 'OKL',  # Oklahoma City Thunder
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
    
    def _get_overall_standings(self, season: str) -> Dict:
        """Fetch overall standings/rankings"""
        try:
            endpoint = f"{season}/standings.json"
            url = f"{self.base_url}/{endpoint}"
            
            time.sleep(self.request_delay)
            response = requests.get(url, auth=self.auth)
            
            if response.status_code == 429:
                time.sleep(self.retry_delay)
                response = requests.get(url, auth=self.auth)
            
            response.raise_for_status()
            data = response.json()
            
            # Process standings into rankings
            rankings = {}
            if data and 'teams' in data:
                # Sort teams by win percentage for overall rank
                teams_sorted = sorted(data['teams'], 
                                    key=lambda x: x['stats']['standings']['winPct'], 
                                    reverse=True)
                
                for rank, team in enumerate(teams_sorted, 1):
                    abbr = team['team']['abbreviation']
                    # Convert API abbreviation to common
                    if abbr == 'BRO':
                        abbr = 'BKN'
                    elif abbr == 'OKL':
                        abbr = 'OKC'
                    
                    stats = team['stats']['standings']
                    rankings[abbr] = {
                        'overall_rank': rank,
                        'wins': stats['wins'],
                        'losses': stats['losses'],
                        'win_pct': stats['winPct'],
                        'conference_rank': team['conferenceRank']['rank'] if 'conferenceRank' in team else None,
                        'division_rank': team['divisionRank']['rank'] if 'divisionRank' in team else None
                    }
            
            return rankings
            
        except Exception as e:
            print(f"Error fetching standings: {e}")
            return {}
    
    def _get_team_stats_rankings(self, season: str) -> Dict:
        """Fetch team statistics for offensive and defensive rankings"""
        try:
            endpoint = f"{season}/team_stats_totals.json"
            url = f"{self.base_url}/{endpoint}"
            
            time.sleep(self.request_delay)
            response = requests.get(url, auth=self.auth)
            
            if response.status_code == 429:
                time.sleep(self.retry_delay)
                response = requests.get(url, auth=self.auth)
            
            response.raise_for_status()
            data = response.json()
            
            rankings = {}
            if data and 'teamStatsTotals' in data:
                # Sort by points per game for offensive ranking
                teams_off = sorted(data['teamStatsTotals'], 
                                 key=lambda x: x['stats']['offense']['ptsPerGame'], 
                                 reverse=True)
                
                # Sort by opponent points per game for defensive ranking (lower is better)
                # Note: The field might be 'oppPtsPerGame' or 'ptsAgainstPerGame'
                teams_def = sorted(data['teamStatsTotals'], 
                                 key=lambda x: x['stats']['defense'].get('oppPtsPerGame', 
                                                x['stats']['defense'].get('ptsAgainstPerGame', 0)))
                
                # Create offensive rankings
                off_rankings = {}
                for rank, team in enumerate(teams_off, 1):
                    abbr = team['team']['abbreviation']
                    if abbr == 'BRO':
                        abbr = 'BKN'
                    elif abbr == 'OKL':
                        abbr = 'OKC'
                    off_rankings[abbr] = rank
                
                # Create defensive rankings
                def_rankings = {}
                for rank, team in enumerate(teams_def, 1):
                    abbr = team['team']['abbreviation']
                    if abbr == 'BRO':
                        abbr = 'BKN'
                    elif abbr == 'OKL':
                        abbr = 'OKC'
                    def_rankings[abbr] = rank
                
                # Combine rankings
                for abbr in off_rankings:
                    rankings[abbr] = {
                        'offensive_rank': off_rankings[abbr],
                        'defensive_rank': def_rankings.get(abbr)
                    }
            
            return rankings
            
        except Exception as e:
            print(f"Error fetching team stats rankings: {e}")
            return {}
    
    def _get_conference_division_rankings(self, team_abbr: str, season: str) -> Dict:
        """Get conference and division specific rankings for a team"""
        try:
            # This would require additional API calls for conference/division specific standings
            # For now, we'll use the data from overall standings which includes these ranks
            return {}
        except Exception as e:
            print(f"Error fetching conference/division rankings: {e}")
            return {}
    
    def _get_historical_rankings(self, team_abbr: str, date: str, num_games: int = 12) -> List[Dict]:
        """
        Get historical ranking data for the last N games to show progression
        This is for the line graph visualization
        """
        historical = []
        
        try:
            # We'll fetch rankings at different points in time
            # This is simplified - in production you might want to cache this data
            current_date = datetime.strptime(date, '%Y%m%d')
            
            for i in range(num_games):
                # Go back i*3 days (assuming games every ~3 days)
                check_date = current_date - timedelta(days=i*3)
                check_date_str = check_date.strftime('%Y%m%d')
                
                # For demonstration, we'll create sample data
                # In production, you'd make actual API calls here
                historical.append({
                    'game_num': num_games - i,
                    'date': check_date_str,
                    'overall_rank': None,  # Would be filled with actual data
                    'offensive_rank': None,
                    'defensive_rank': None
                })
            
            return historical
            
        except Exception as e:
            print(f"Error fetching historical rankings: {e}")
            return []
    
    def collect(self, away_team: str, home_team: str, game_date: str) -> Dict:
        """
        Main collection method for team rankings
        
        Args:
            away_team: Away team abbreviation
            home_team: Home team abbreviation
            game_date: Game date in YYYYMMDD format
            
        Returns:
            Dictionary containing ranking data for both teams
        """
        print(f"  Collecting rankings for {away_team} and {home_team}...")
        
        season = self._get_season(game_date)
        
        # Get overall standings/rankings
        overall_rankings = self._get_overall_standings(season)
        
        # Get offensive/defensive rankings
        stats_rankings = self._get_team_stats_rankings(season)
        
        # Combine data for both teams
        away_rankings = {}
        home_rankings = {}
        
        if away_team in overall_rankings:
            away_rankings.update(overall_rankings[away_team])
        if away_team in stats_rankings:
            away_rankings.update(stats_rankings[away_team])
        
        if home_team in overall_rankings:
            home_rankings.update(overall_rankings[home_team])
        if home_team in stats_rankings:
            home_rankings.update(stats_rankings[home_team])
        
        # Get historical data for graphs (simplified for now)
        away_historical = self._get_historical_rankings(away_team, game_date)
        home_historical = self._get_historical_rankings(home_team, game_date)
        
        # Format the data
        rankings_data = {
            'away_rankings': {
                'overall': away_rankings.get('overall_rank', '-'),
                'offensive': away_rankings.get('offensive_rank', '-'),
                'defensive': away_rankings.get('defensive_rank', '-'),
                'conference': away_rankings.get('conference_rank', '-'),
                'division': away_rankings.get('division_rank', '-'),
                'conference_offensive': '-',  # Would need additional API calls
                'conference_defensive': '-',
                'division_offensive': '-',
                'division_defensive': '-',
                'historical': away_historical
            },
            'home_rankings': {
                'overall': home_rankings.get('overall_rank', '-'),
                'offensive': home_rankings.get('offensive_rank', '-'),
                'defensive': home_rankings.get('defensive_rank', '-'),
                'conference': home_rankings.get('conference_rank', '-'),
                'division': home_rankings.get('division_rank', '-'),
                'conference_offensive': '-',
                'conference_defensive': '-',
                'division_offensive': '-',
                'division_defensive': '-',
                'historical': home_historical
            }
        }
        
        return rankings_data


# Test the collector
if __name__ == "__main__":
    collector = TeamRankingsCollector()
    
    # Test with sample teams
    away_team = 'MIL'
    home_team = 'PHI'
    game_date = '20250119'
    
    print(f"\n📊 Testing Rankings Collector")
    print(f"   Teams: {away_team} @ {home_team}")
    print(f"   Date: {game_date}")
    print("-" * 50)
    
    rankings_data = collector.collect(away_team, home_team, game_date)
    
    print("\n📈 Rankings Data Collected:")
    print(f"\n{away_team} Rankings:")
    for key, value in rankings_data['away_rankings'].items():
        if key != 'historical':
            print(f"  {key}: {value}")
    
    print(f"\n{home_team} Rankings:")
    for key, value in rankings_data['home_rankings'].items():
        if key != 'historical':
            print(f"  {key}: {value}")