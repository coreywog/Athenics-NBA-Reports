#!/usr/bin/env python3
"""
Game Header Collector - Enhanced Version with Home/Away Statistics
Includes home and away records, streaks, vs conference records, and abbreviation conversion
"""

import os
import requests
from datetime import datetime
from typing import Dict, Optional, Tuple, List
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from pathlib import Path
import time

load_dotenv()

class GameHeaderCollector:
    """Collects data for the game header section with enhanced home/away statistics"""
    
    def __init__(self):
        self.api_key = os.getenv('MSF_API_KEY')
        self.password = os.getenv('MSF_PASSWORD', 'MYSPORTSFEEDS')
        self.base_url = 'https://api.mysportsfeeds.com/v2.1/pull/nba'
        self.auth = HTTPBasicAuth(self.api_key, self.password)
        
        # API abbreviation to common abbreviation mapping
        self.api_to_common = {
            'BRO': 'BKN',  # Brooklyn Nets
            'OKL': 'OKC',  # Oklahoma City Thunder
        }
        
        # Common abbreviation to API abbreviation mapping (reverse)
        self.common_to_api = {
            'BKN': 'BRO',  # Brooklyn Nets
            'OKC': 'OKL',  # Oklahoma City Thunder
        }
        
        # Team information mapping (using COMMON abbreviations for display)
        self.team_info = {
            'ATL': {'name': 'Hawks', 'city': 'Atlanta', 'state': 'GA', 'conf': 'Eastern', 'div': 'Southeast'},
            'BOS': {'name': 'Celtics', 'city': 'Boston', 'state': 'MA', 'conf': 'Eastern', 'div': 'Atlantic'},
            'BKN': {'name': 'Nets', 'city': 'Brooklyn', 'state': 'NY', 'conf': 'Eastern', 'div': 'Atlantic'},  # Common abbreviation
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
            'OKC': {'name': 'Thunder', 'city': 'Oklahoma City', 'state': 'OK', 'conf': 'Western', 'div': 'Northwest'},  # Common abbreviation
            'ORL': {'name': 'Magic', 'city': 'Orlando', 'state': 'FL', 'conf': 'Eastern', 'div': 'Southeast'},
            'PHI': {'name': '76ers', 'city': 'Philadelphia', 'state': 'PA', 'conf': 'Eastern', 'div': 'Atlantic'},
            'PHX': {'name': 'Suns', 'city': 'Phoenix', 'state': 'AZ', 'conf': 'Western', 'div': 'Pacific'},
            'POR': {'name': 'Trail Blazers', 'city': 'Portland', 'state': 'OR', 'conf': 'Western', 'div': 'Northwest'},
            'SAC': {'name': 'Kings', 'city': 'Sacramento', 'state': 'CA', 'conf': 'Western', 'div': 'Pacific'},
            'SAS': {'name': 'Spurs', 'city': 'San Antonio', 'state': 'TX', 'conf': 'Western', 'div': 'Southwest'},
            'TOR': {'name': 'Raptors', 'city': 'Toronto', 'state': 'ON', 'conf': 'Eastern', 'div': 'Atlantic'},
            'UTA': {'name': 'Jazz', 'city': 'Utah', 'state': 'UT', 'conf': 'Western', 'div': 'Northwest'},
            'WAS': {'name': 'Wizards', 'city': 'Washington', 'state': 'DC', 'conf': 'Eastern', 'div': 'Southeast'},
            # Keep API abbreviations as fallbacks for internal lookups
            'BRO': {'name': 'Nets', 'city': 'Brooklyn', 'state': 'NY', 'conf': 'Eastern', 'div': 'Atlantic'},
            'OKL': {'name': 'Thunder', 'city': 'Oklahoma City', 'state': 'OK', 'conf': 'Western', 'div': 'Northwest'}
        }
    
    def _convert_to_common_abbr(self, api_abbr: str) -> str:
        """Convert API abbreviation to common abbreviation"""
        return self.api_to_common.get(api_abbr, api_abbr)
    
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
                            formatted_time = time_obj.strftime('%I:%M %p EST').lstrip('0')
                        except:
                            formatted_time = 'TBD'
                    else:
                        formatted_time = 'TBD'
                    
                    return {
                        'date': formatted_date,
                        'time': formatted_time,
                        'venue': schedule.get('venue', {}).get('name', 'TBD'),
                        'city': home_team
                    }
        
        # If no game found, still format the date nicely
        try:
            date_obj = datetime.strptime(date, '%Y%m%d')
            formatted_date = date_obj.strftime('%B %d, %Y')
        except:
            formatted_date = date
            
        return {'date': formatted_date, 'time': 'TBD', 'venue': 'TBD', 'city': ''}
    
    def _calculate_home_away_records(self, team: str, season: str, date: str) -> Tuple[str, str]:
        """Calculate home and away records for a team"""
        endpoint = f"{season}/games.json"
        params = {'team': team}
        
        if date and date != '20250119':
            params['date'] = f'until-{date}'
        
        data = self._make_request(endpoint, params)
        
        home_wins = 0
        home_losses = 0
        away_wins = 0
        away_losses = 0
        
        if data and 'games' in data:
            for game in data['games']:
                schedule = game.get('schedule', {})
                score = game.get('score', {})
                
                # Only count completed games
                if not score or schedule.get('playedStatus') != 'COMPLETED':
                    continue
                
                away_team = schedule.get('awayTeam', {}).get('abbreviation')
                home_team = schedule.get('homeTeam', {}).get('abbreviation')
                away_score = score.get('awayScoreTotal', 0)
                home_score = score.get('homeScoreTotal', 0)
                
                if away_team == team:
                    # Team played away
                    if away_score > home_score:
                        away_wins += 1
                    else:
                        away_losses += 1
                elif home_team == team:
                    # Team played at home
                    if home_score > away_score:
                        home_wins += 1
                    else:
                        home_losses += 1
        
        return f"{home_wins}-{home_losses}", f"{away_wins}-{away_losses}"
    
    def _calculate_vs_conference_records(self, team: str, season: str, date: str) -> Tuple[str, str]:
        """Calculate records vs Eastern and Western conferences"""
        endpoint = f"{season}/games.json"
        params = {'team': team}
        
        if date and date != '20250119':
            params['date'] = f'until-{date}'
        
        data = self._make_request(endpoint, params)
        
        eastern_wins = 0
        eastern_losses = 0
        western_wins = 0
        western_losses = 0
        
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
                # Convert API abbreviation to common for team_info lookup
                opponent_common = self._convert_to_common_abbr(opponent)
                opponent_conf = self.team_info.get(opponent_common, {}).get('conf')
                
                if not opponent_conf:
                    # Try with the original abbreviation as fallback
                    opponent_conf = self.team_info.get(opponent, {}).get('conf')
                
                if not opponent_conf:
                    continue
                
                away_score = score.get('awayScoreTotal', 0)
                home_score = score.get('homeScoreTotal', 0)
                
                # Determine if team won
                team_won = False
                if away_team == team:
                    team_won = away_score > home_score
                else:
                    team_won = home_score > away_score
                
                # Add to appropriate conference record
                if opponent_conf == 'Eastern':
                    if team_won:
                        eastern_wins += 1
                    else:
                        eastern_losses += 1
                elif opponent_conf == 'Western':
                    if team_won:
                        western_wins += 1
                    else:
                        western_losses += 1
        
        return f"{eastern_wins}-{eastern_losses}", f"{western_wins}-{western_losses}"
    
    def _calculate_recent_records_and_streak(self, team: str, season: str, date: str) -> Dict[str, str]:
        """Calculate last 3, 7, 12 games records and current streak"""
        endpoint = f"{season}/games.json"
        params = {'team': team}
        
        if date and date != '20250119':
            params['date'] = f'until-{date}'
        
        data = self._make_request(endpoint, params)
        
        games_results = []  # List of True (win) or False (loss)
        
        if data and 'games' in data:
            # Sort games by date to get chronological order
            sorted_games = []
            for game in data['games']:
                schedule = game.get('schedule', {})
                score = game.get('score', {})
                
                # Only count completed games
                if not score or schedule.get('playedStatus') != 'COMPLETED':
                    continue
                
                game_id = schedule.get('id', '')
                if game_id:
                    game_date = str(game_id).split('-')[0] if '-' in str(game_id) else ''
                    sorted_games.append((game_date, game))
            
            sorted_games.sort(key=lambda x: x[0])
            
            # Process games in chronological order
            for _, game in sorted_games:
                schedule = game['schedule']
                score = game['score']
                
                away_team = schedule.get('awayTeam', {}).get('abbreviation')
                home_team = schedule.get('homeTeam', {}).get('abbreviation')
                away_score = score.get('awayScoreTotal', 0)
                home_score = score.get('homeScoreTotal', 0)
                
                if away_team == team:
                    games_results.append(away_score > home_score)
                elif home_team == team:
                    games_results.append(home_score > away_score)
        
        # Calculate last 3, 7, and 12
        last_3_wins = 0
        last_3_losses = 0
        last_7_wins = 0
        last_7_losses = 0
        last_12_wins = 0
        last_12_losses = 0
        
        if len(games_results) > 0:
            # Last 3 games
            last_3_results = games_results[-3:]
            last_3_wins = sum(last_3_results)
            last_3_losses = len(last_3_results) - last_3_wins
            
            # Last 7 games
            last_7_results = games_results[-7:]
            last_7_wins = sum(last_7_results)
            last_7_losses = len(last_7_results) - last_7_wins
            
            # Last 12 games
            last_12_results = games_results[-12:]
            last_12_wins = sum(last_12_results)
            last_12_losses = len(last_12_results) - last_12_wins
        
        # Calculate current streak
        streak = ""
        if len(games_results) > 0:
            current_result = games_results[-1]
            streak_count = 1
            
            # Count consecutive same results from the end
            for i in range(len(games_results) - 2, -1, -1):
                if games_results[i] == current_result:
                    streak_count += 1
                else:
                    break
            
            streak_type = "W" if current_result else "L"
            streak = f"{streak_type}{streak_count}"
        
        return {
            'last_3': f"{last_3_wins}-{last_3_losses}",
            'last_7': f"{last_7_wins}-{last_7_losses}",
            'last_12': f"{last_12_wins}-{last_12_losses}",
            'streak': streak
        }
    
    def get_team_records(self, team: str, season: str, date: str) -> Dict:
        """Get comprehensive team records including home/away and vs conferences"""
        # Get overall record from standings
        overall_record = self._get_overall_record(team, season)
        
        # Calculate conference and division records
        conf_record = self._calculate_conference_record(team, season, date)
        div_record = self._calculate_division_record(team, season, date)
        
        # Calculate home and away records
        home_record, away_record = self._calculate_home_away_records(team, season, date)
        
        # Calculate vs conference records
        vs_eastern, vs_western = self._calculate_vs_conference_records(team, season, date)
        
        # Calculate recent records and streak
        recent_records = self._calculate_recent_records_and_streak(team, season, date)
        
        return {
            'overall': overall_record,
            'conference': conf_record,
            'division': div_record,
            'home': home_record,
            'away': away_record,
            'vs_eastern': vs_eastern,
            'vs_western': vs_western,
            'last_3': recent_records['last_3'],
            'last_7': recent_records['last_7'],
            'last_12': recent_records['last_12'],
            'streak': recent_records['streak']
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
        # Convert to common abbreviation to get conference info
        team_common = self._convert_to_common_abbr(team)
        team_conf = self.team_info.get(team_common, {}).get('conf')
        
        if not team_conf:
            # Try with original abbreviation as fallback
            team_conf = self.team_info.get(team, {}).get('conf')
        
        if not team_conf:
            return "0-0"
        
        endpoint = f"{season}/games.json"
        params = {'team': team}
        
        if date and date != '20250119':
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
                # Convert to common abbreviation for team_info lookup
                opponent_common = self._convert_to_common_abbr(opponent)
                opponent_conf = self.team_info.get(opponent_common, {}).get('conf')
                
                if not opponent_conf:
                    # Try with original abbreviation as fallback
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
        # Convert to common abbreviation to get division info
        team_common = self._convert_to_common_abbr(team)
        team_div = self.team_info.get(team_common, {}).get('div')
        
        if not team_div:
            # Try with original abbreviation as fallback
            team_div = self.team_info.get(team, {}).get('div')
        
        if not team_div:
            return "0-0"
        
        endpoint = f"{season}/games.json"
        params = {'team': team}
        
        if date and date != '20250119':
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
                # Convert to common abbreviation for team_info lookup
                opponent_common = self._convert_to_common_abbr(opponent)
                opponent_div = self.team_info.get(opponent_common, {}).get('div')
                
                if not opponent_div:
                    # Try with original abbreviation as fallback
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
                            game_date = parts[0]
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
        Collect all header section data with enhanced statistics
        
        Args:
            away_team: Away team abbreviation (can be common or API format)
            home_team: Home team abbreviation (can be common or API format)
            date: Date in YYYYMMDD format
        
        Returns complete data for the game header section including home/away records
        """
        # Convert to API abbreviations for API calls
        away_api = self._convert_to_api_abbr(away_team)
        home_api = self._convert_to_api_abbr(home_team)
        
        # Convert to common abbreviations for display
        away_common = self._convert_to_common_abbr(away_api)
        home_common = self._convert_to_common_abbr(home_api)
        
        print(f"Collecting game header for {away_common} @ {home_common} on {date}")
        
        season = self._get_season(date)
        
        # Use API abbreviations for API calls
        game_info = self.get_game_info(away_api, home_api, date)
        
        # Get team information using common abbreviations
        away_info = self.team_info.get(away_common, {})
        home_info = self.team_info.get(home_common, {})
        
        print("Getting comprehensive team records (this may take a moment)...")
        # Get all records using API abbreviations
        away_records = self.get_team_records(away_api, season, date)
        home_records = self.get_team_records(home_api, season, date)
        
        # Get H2H record using API abbreviations
        h2h_record = self.get_h2h_season_record(away_api, home_api, season, date)
        
        return {
            'game_info': {
                'city_state': f"{home_info.get('city', '')}, {home_info.get('state', '')}",
                'date': game_info['date'],
                'time': game_info['time'],
                'stadium': game_info['venue']
            },
            'away_team': {
                'abbreviation': away_common,  # Use common abbreviation for display
                'name': away_info.get('name', ''),
                'city_state': f"{away_info.get('city', '')}, {away_info.get('state', '')}",
                'conference': away_info.get('conf', ''),
                'division': away_info.get('div', ''),
                'logo_path': f"assets/teams/{away_common}.png",  # Use common abbreviation for logo
                'records': away_records
            },
            'home_team': {
                'abbreviation': home_common,  # Use common abbreviation for display
                'name': home_info.get('name', ''),
                'city_state': f"{home_info.get('city', '')}, {home_info.get('state', '')}",
                'conference': home_info.get('conf', ''),
                'division': home_info.get('div', ''),
                'logo_path': f"assets/teams/{home_common}.png",  # Use common abbreviation for logo
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
    print("\nEnhanced Game Header Data:")
    print("=" * 60)
    print(json.dumps(data, indent=2))