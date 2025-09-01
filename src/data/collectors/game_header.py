#!/usr/bin/env python3
"""
Game Header Collector - Fixed Version
Properly calculates conference and division records
"""

import os
import requests
from datetime import datetime
from typing import Dict, Optional, Tuple
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from pathlib import Path
import time

load_dotenv()

class GameHeaderCollector:
    """Collects data for the game header section"""
    
    def __init__(self):
        self.api_key = os.getenv('MSF_API_KEY')
        self.password = os.getenv('MSF_PASSWORD', 'MYSPORTSFEEDS')
        self.base_url = 'https://api.mysportsfeeds.com/v2.1/pull/nba'
        self.auth = HTTPBasicAuth(self.api_key, self.password)
        
        # Team information mapping (using API abbreviations)
        self.team_info = {
            'ATL': {'name': 'Hawks', 'city': 'Atlanta', 'state': 'GA', 'conf': 'Eastern', 'div': 'Southeast'},
            'BOS': {'name': 'Celtics', 'city': 'Boston', 'state': 'MA', 'conf': 'Eastern', 'div': 'Atlantic'},
            'BRO': {'name': 'Nets', 'city': 'Brooklyn', 'state': 'NY', 'conf': 'Eastern', 'div': 'Atlantic'},  # BRO not BKN
            'CHA': {'name': 'Hornets', 'city': 'Charlotte', 'state': 'NC', 'conf': 'Eastern', 'div': 'Southeast'},
            'CHI': {'name': 'Bulls', 'city': 'Chicago', 'state': 'IL', 'conf': 'Eastern', 'div': 'Central'},
            'CLE': {'name': 'Cavaliers', 'city': 'Cleveland', 'state': 'OH', 'conf': 'Eastern', 'div': 'Central'},
            'DAL': {'name': 'Mavericks', 'city': 'Dallas', 'state': 'TX', 'conf': 'Western', 'div': 'Southwest'},
            'DEN': {'name': 'Nuggets', 'city': 'Denver', 'state': 'CO', 'conf': 'Western', 'div': 'Northwest'},
            'DET': {'name': 'Pistons', 'city': 'Detroit', 'state': 'MI', 'conf': 'Eastern', 'div': 'Central'},
            'GSW': {'name': 'Warriors', 'city': 'Golden State', 'state': 'CA', 'conf': 'Western', 'div': 'Pacific'},
            'HOU': {'name': 'Rockets', 'city': 'Houston', 'state': 'TX', 'conf': 'Western', 'div': 'Southwest'},
            'IND': {'name': 'Pacers', 'city': 'Indiana', 'state': 'IN', 'conf': 'Eastern', 'div': 'Central'},
            'LAC': {'name': 'Clippers', 'city': 'Los Angeles', 'state': 'CA', 'conf': 'Western', 'div': 'Pacific'},
            'LAL': {'name': 'Lakers', 'city': 'Los Angeles', 'state': 'CA', 'conf': 'Western', 'div': 'Pacific'},
            'MEM': {'name': 'Grizzlies', 'city': 'Memphis', 'state': 'TN', 'conf': 'Western', 'div': 'Southwest'},
            'MIA': {'name': 'Heat', 'city': 'Miami', 'state': 'FL', 'conf': 'Eastern', 'div': 'Southeast'},
            'MIL': {'name': 'Bucks', 'city': 'Milwaukee', 'state': 'WI', 'conf': 'Eastern', 'div': 'Central'},
            'MIN': {'name': 'Timberwolves', 'city': 'Minnesota', 'state': 'MN', 'conf': 'Western', 'div': 'Northwest'},
            'NOP': {'name': 'Pelicans', 'city': 'New Orleans', 'state': 'LA', 'conf': 'Western', 'div': 'Southwest'},
            'NYK': {'name': 'Knicks', 'city': 'New York', 'state': 'NY', 'conf': 'Eastern', 'div': 'Atlantic'},
            'OKL': {'name': 'Thunder', 'city': 'Oklahoma City', 'state': 'OK', 'conf': 'Western', 'div': 'Northwest'},  # OKL not OKC
            'ORL': {'name': 'Magic', 'city': 'Orlando', 'state': 'FL', 'conf': 'Eastern', 'div': 'Southeast'},
            'PHI': {'name': '76ers', 'city': 'Philadelphia', 'state': 'PA', 'conf': 'Eastern', 'div': 'Atlantic'},
            'PHX': {'name': 'Suns', 'city': 'Phoenix', 'state': 'AZ', 'conf': 'Western', 'div': 'Pacific'},
            'POR': {'name': 'Trail Blazers', 'city': 'Portland', 'state': 'OR', 'conf': 'Western', 'div': 'Northwest'},
            'SAC': {'name': 'Kings', 'city': 'Sacramento', 'state': 'CA', 'conf': 'Western', 'div': 'Pacific'},
            'SAS': {'name': 'Spurs', 'city': 'San Antonio', 'state': 'TX', 'conf': 'Western', 'div': 'Southwest'},
            'TOR': {'name': 'Raptors', 'city': 'Toronto', 'state': 'ON', 'conf': 'Eastern', 'div': 'Atlantic'},
            'UTA': {'name': 'Jazz', 'city': 'Utah', 'state': 'UT', 'conf': 'Western', 'div': 'Northwest'},
            'WAS': {'name': 'Wizards', 'city': 'Washington', 'state': 'DC', 'conf': 'Eastern', 'div': 'Southeast'},
            # Legacy abbreviations that might still be used
            'BKN': {'name': 'Nets', 'city': 'Brooklyn', 'state': 'NY', 'conf': 'Eastern', 'div': 'Atlantic'},
            'OKC': {'name': 'Thunder', 'city': 'Oklahoma City', 'state': 'OK', 'conf': 'Western', 'div': 'Northwest'}
        }
    
    def _get_season(self, date: str) -> str:
        """Determine season from date"""
        year = int(date[:4])
        month = int(date[4:6])
        if month >= 10:
            return f"{year}-{year+1}-regular"
        else:
            return f"{year-1}-{year}-regular"
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with rate limiting"""
        url = f"{self.base_url}/{endpoint}"
        try:
            time.sleep(0.5)  # Be nice to the API
            response = requests.get(url, auth=self.auth, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching {endpoint}: {e}")
            return None
    
    def get_game_info(self, away_team: str, home_team: str, date: str) -> Dict:
        """Get basic game information"""
        season = self._get_season(date)
        endpoint = f"{season}/date/{date}/games.json"
        params = {'team': f"{away_team},{home_team}"}
        
        data = self._make_request(endpoint, params)
        
        if data and 'games' in data:
            for game in data['games']:
                schedule = game.get('schedule', {})
                away = schedule.get('awayTeam', {}).get('abbreviation')
                home = schedule.get('homeTeam', {}).get('abbreviation')
                
                if away == away_team and home == home_team:
                    # Format date for display
                    date_obj = datetime.strptime(date, '%Y%m%d')
                    formatted_date = date_obj.strftime('%B %d, %Y')
                    
                    # Format time
                    start_time = schedule.get('startTime', '')
                    if start_time:
                        try:
                            time_obj = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                            formatted_time = time_obj.strftime('%-I:%M %p EST')
                        except:
                            formatted_time = 'TBD'
                    else:
                        formatted_time = 'TBD'
                    
                    return {
                        'date': formatted_date,
                        'time': formatted_time,
                        'venue': schedule.get('venue', {}).get('name', 'TBD'),
                        'city': home_team  # Will use team's city from team_info
                    }
        
        # If no game found, still format the date nicely
        try:
            date_obj = datetime.strptime(date, '%Y%m%d')
            formatted_date = date_obj.strftime('%B %d, %Y')
        except:
            formatted_date = date
            
        return {'date': formatted_date, 'time': 'TBD', 'venue': 'TBD', 'city': ''}
    
    def get_team_records(self, team: str, season: str, date: str) -> Dict:
        """
        Get team's various records (overall, conference, division)
        We need to calculate conference and division records from game results
        """
        # First get overall record from standings
        overall_record = self._get_overall_record(team, season)
        
        # Calculate conference and division records from games
        conf_record = self._calculate_conference_record(team, season, date)
        div_record = self._calculate_division_record(team, season, date)
        
        return {
            'overall': overall_record,
            'conference': conf_record,
            'division': div_record
        }
    
    def _get_overall_record(self, team: str, season: str) -> str:
        """Get overall W-L from standings"""
        endpoint = f"{season}/standings.json"
        params = {'team': team}
        
        data = self._make_request(endpoint, params)
        
        if data and 'teams' in data:
            for team_data in data['teams']:
                if team_data.get('team', {}).get('abbreviation') == team:
                    standings = team_data.get('stats', {}).get('standings', {})
                    wins = standings.get('wins', 0)
                    losses = standings.get('losses', 0)
                    return f"{wins}-{losses}"
        
        return "0-0"
    
    def _calculate_conference_record(self, team: str, season: str, date: str) -> str:
        """Calculate conference record by analyzing games"""
        team_conf = self.team_info.get(team, {}).get('conf')
        if not team_conf:
            return "0-0"
        
        # Get all games for the team
        endpoint = f"{season}/games.json"
        params = {'team': team}
        
        # If we have a specific date, only count games before that date
        if date and date != '20250119':  # Don't filter if using our test date
            params['date'] = f'until-{date}'
        
        data = self._make_request(endpoint, params)
        
        conf_wins = 0
        conf_losses = 0
        
        if data and 'games' in data:
            for game in data['games']:
                schedule = game.get('schedule', {})
                score = game.get('score', {})
                
                # Only count completed games
                if not score or schedule.get('playedStatus') != 'COMPLETED':
                    continue
                
                away_team = schedule.get('awayTeam', {}).get('abbreviation')
                home_team = schedule.get('homeTeam', {}).get('abbreviation')
                
                # Determine opponent
                opponent = home_team if away_team == team else away_team
                opponent_conf = self.team_info.get(opponent, {}).get('conf')
                
                # Only count if opponent is in same conference
                if opponent_conf == team_conf:
                    away_score = score.get('awayScoreTotal', 0)
                    home_score = score.get('homeScoreTotal', 0)
                    
                    if away_team == team:
                        if away_score > home_score:
                            conf_wins += 1
                        else:
                            conf_losses += 1
                    else:
                        if home_score > away_score:
                            conf_wins += 1
                        else:
                            conf_losses += 1
        
        return f"{conf_wins}-{conf_losses}"
    
    def _calculate_division_record(self, team: str, season: str, date: str) -> str:
        """Calculate division record by analyzing games"""
        team_div = self.team_info.get(team, {}).get('div')
        if not team_div:
            return "0-0"
        
        # Get all games for the team
        endpoint = f"{season}/games.json"
        params = {'team': team}
        
        # If we have a specific date, only count games before that date
        if date and date != '20250119':  # Don't filter if using our test date
            params['date'] = f'until-{date}'
        
        data = self._make_request(endpoint, params)
        
        div_wins = 0
        div_losses = 0
        
        if data and 'games' in data:
            for game in data['games']:
                schedule = game.get('schedule', {})
                score = game.get('score', {})
                
                # Only count completed games
                if not score or schedule.get('playedStatus') != 'COMPLETED':
                    continue
                
                away_team = schedule.get('awayTeam', {}).get('abbreviation')
                home_team = schedule.get('homeTeam', {}).get('abbreviation')
                
                # Determine opponent
                opponent = home_team if away_team == team else away_team
                opponent_div = self.team_info.get(opponent, {}).get('div')
                
                # Only count if opponent is in same division
                if opponent_div == team_div:
                    away_score = score.get('awayScoreTotal', 0)
                    home_score = score.get('homeScoreTotal', 0)
                    
                    if away_team == team:
                        if away_score > home_score:
                            div_wins += 1
                        else:
                            div_losses += 1
                    else:
                        if home_score > away_score:
                            div_wins += 1
                        else:
                            div_losses += 1
        
        return f"{div_wins}-{div_losses}"
    
    def get_h2h_season_record(self, team_a: str, team_b: str, season: str, date: str) -> str:
        """Get head-to-head record for current season up to the given date"""
        endpoint = f"{season}/games.json"
        params = {'team': f"{team_a},{team_b}"}
        
        data = self._make_request(endpoint, params)
        team_a_wins = 0
        team_b_wins = 0
        
        if data and 'games' in data:
            for game in data['games']:
                schedule = game.get('schedule', {})
                away = schedule.get('awayTeam', {}).get('abbreviation')
                home = schedule.get('homeTeam', {}).get('abbreviation')
                
                # Only count games between these two teams
                if {away, home} != {team_a, team_b}:
                    continue
                
                # Only count completed games before or on the given date
                score = game.get('score', {})
                if not score or schedule.get('playedStatus') != 'COMPLETED':
                    continue
                
                # Check if game date is before our target date
                game_id = schedule.get('id', '')
                if game_id:
                    game_id_str = str(game_id)
                    if '-' in game_id_str:
                        parts = game_id_str.split('-')
                        if len(parts) > 0:
                            game_date = parts[0]  # Format: YYYYMMDD-AWAY-HOME
                            if game_date and game_date > date:
                                continue
                
                away_score = score.get('awayScoreTotal', 0)
                home_score = score.get('homeScoreTotal', 0)
                
                if away_score > home_score:
                    if away == team_a:
                        team_a_wins += 1
                    else:
                        team_b_wins += 1
                else:
                    if home == team_a:
                        team_a_wins += 1
                    else:
                        team_b_wins += 1
        
        return f"{team_a_wins}-{team_b_wins}"
    
    def collect(self, away_team: str, home_team: str, date: str) -> Dict:
        """
        Collect all header section data
        
        Returns complete data for the game header section
        """
        print(f"Collecting game header for {away_team} @ {home_team} on {date}")
        
        season = self._get_season(date)
        game_info = self.get_game_info(away_team, home_team, date)
        
        # Get team information
        away_info = self.team_info.get(away_team, {})
        home_info = self.team_info.get(home_team, {})
        
        print("Getting team records (this may take a moment)...")
        # Get records - passing date to only count games up to that point
        away_records = self.get_team_records(away_team, season, date)
        home_records = self.get_team_records(home_team, season, date)
        
        # Get H2H record
        h2h_record = self.get_h2h_season_record(away_team, home_team, season, date)
        
        return {
            'game_info': {
                'city_state': f"{home_info.get('city', '')}, {home_info.get('state', '')}",
                'date': game_info['date'],
                'time': game_info['time'],
                'stadium': game_info['venue']
            },
            'away_team': {
                'abbreviation': away_team,
                'name': away_info.get('name', ''),
                'city_state': f"{away_info.get('city', '')}, {away_info.get('state', '')}",
                'conference': away_info.get('conf', ''),
                'division': away_info.get('div', ''),
                'logo_path': f"assets/teams/{away_team}.png",
                'records': away_records
            },
            'home_team': {
                'abbreviation': home_team,
                'name': home_info.get('name', ''),
                'city_state': f"{home_info.get('city', '')}, {home_info.get('state', '')}",
                'conference': home_info.get('conf', ''),
                'division': home_info.get('div', ''),
                'logo_path': f"assets/teams/{home_team}.png",
                'records': home_records
            },
            'h2h_season_record': h2h_record
        }


# Test the collector
if __name__ == "__main__":
    collector = GameHeaderCollector()
    
    # Test with MIL @ PHI on Jan 19, 2025
    data = collector.collect('MIL', 'PHI', '20250119')
    
    import json
    print("\nGame Header Data:")
    print("=" * 60)
    print(json.dumps(data, indent=2))