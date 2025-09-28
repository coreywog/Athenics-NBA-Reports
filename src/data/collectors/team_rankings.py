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
            response = requests.get(url, auth=self.auth, timeout=10)
            
            if response.status_code == 429:
                time.sleep(self.retry_delay)
                response = requests.get(url, auth=self.auth, timeout=10)
            
            response.raise_for_status()
            data = response.json()
            
            # Define conference and division mappings
            eastern_teams = ['ATL', 'BOS', 'BKN', 'BRO', 'CHA', 'CHI', 'CLE', 'DET', 'IND', 'MIA', 'MIL', 'NYK', 'ORL', 'PHI', 'TOR', 'WAS']
            western_teams = ['DAL', 'DEN', 'GSW', 'HOU', 'LAC', 'LAL', 'MEM', 'MIN', 'NOP', 'OKC', 'OKL', 'PHX', 'POR', 'SAC', 'SAS', 'UTA']
            
            divisions = {
                'Atlantic': ['BOS', 'BKN', 'BRO', 'NYK', 'PHI', 'TOR'],
                'Central': ['CHI', 'CLE', 'DET', 'IND', 'MIL'],
                'Southeast': ['ATL', 'CHA', 'MIA', 'ORL', 'WAS'],
                'Northwest': ['DEN', 'MIN', 'OKC', 'OKL', 'POR', 'UTA'],
                'Pacific': ['GSW', 'LAC', 'LAL', 'PHX', 'SAC'],
                'Southwest': ['DAL', 'HOU', 'MEM', 'NOP', 'SAS']
            }
            
            rankings = {}
            if data and 'teamStatsTotals' in data:
                all_teams = data['teamStatsTotals']
                
                # Overall rankings
                teams_off = sorted(all_teams, key=lambda x: x['stats']['offense']['ptsPerGame'], reverse=True)
                teams_def = sorted(all_teams, key=lambda x: x['stats']['defense'].get('oppPtsPerGame', x['stats']['defense'].get('ptsAgainstPerGame', 0)))
                
                # Conference rankings
                eastern_off = sorted([t for t in all_teams if t['team']['abbreviation'] in eastern_teams or (t['team']['abbreviation'] == 'BRO' and 'BKN' in eastern_teams)], 
                                key=lambda x: x['stats']['offense']['ptsPerGame'], reverse=True)
                eastern_def = sorted([t for t in all_teams if t['team']['abbreviation'] in eastern_teams or (t['team']['abbreviation'] == 'BRO' and 'BKN' in eastern_teams)], 
                                key=lambda x: x['stats']['defense'].get('oppPtsPerGame', 0))
                
                western_off = sorted([t for t in all_teams if t['team']['abbreviation'] in western_teams or (t['team']['abbreviation'] == 'OKL' and 'OKC' in western_teams)], 
                                key=lambda x: x['stats']['offense']['ptsPerGame'], reverse=True)
                western_def = sorted([t for t in all_teams if t['team']['abbreviation'] in western_teams or (t['team']['abbreviation'] == 'OKL' and 'OKC' in western_teams)], 
                                key=lambda x: x['stats']['defense'].get('oppPtsPerGame', 0))
                
                # Process all rankings
                for team in all_teams:
                    abbr = team['team']['abbreviation']
                    if abbr == 'BRO':
                        abbr = 'BKN'
                    elif abbr == 'OKL':
                        abbr = 'OKC'
                    
                    # Find overall ranks
                    overall_off_rank = next((i for i, t in enumerate(teams_off, 1) if t['team']['abbreviation'] == team['team']['abbreviation']), None)
                    overall_def_rank = next((i for i, t in enumerate(teams_def, 1) if t['team']['abbreviation'] == team['team']['abbreviation']), None)
                    
                    # Find conference ranks
                    if abbr in eastern_teams:
                        conf_off_rank = next((i for i, t in enumerate(eastern_off, 1) if t['team']['abbreviation'] == team['team']['abbreviation']), None)
                        conf_def_rank = next((i for i, t in enumerate(eastern_def, 1) if t['team']['abbreviation'] == team['team']['abbreviation']), None)
                    else:
                        conf_off_rank = next((i for i, t in enumerate(western_off, 1) if t['team']['abbreviation'] == team['team']['abbreviation']), None)
                        conf_def_rank = next((i for i, t in enumerate(western_def, 1) if t['team']['abbreviation'] == team['team']['abbreviation']), None)
                    
                    # Find division
                    team_division = None
                    for div_name, teams in divisions.items():
                        if abbr in teams:
                            team_division = div_name
                            break
                    
                    # Calculate division ranks
                    div_off_rank = None
                    div_def_rank = None
                    if team_division:
                        div_teams = divisions[team_division]
                        division_off = sorted([t for t in all_teams if t['team']['abbreviation'] in div_teams or (t['team']['abbreviation'] == 'BRO' and 'BKN' in div_teams) or (t['team']['abbreviation'] == 'OKL' and 'OKC' in div_teams)], 
                                            key=lambda x: x['stats']['offense']['ptsPerGame'], reverse=True)
                        division_def = sorted([t for t in all_teams if t['team']['abbreviation'] in div_teams or (t['team']['abbreviation'] == 'BRO' and 'BKN' in div_teams) or (t['team']['abbreviation'] == 'OKL' and 'OKC' in div_teams)], 
                                            key=lambda x: x['stats']['defense'].get('oppPtsPerGame', 0))
                        
                        div_off_rank = next((i for i, t in enumerate(division_off, 1) if t['team']['abbreviation'] == team['team']['abbreviation']), None)
                        div_def_rank = next((i for i, t in enumerate(division_def, 1) if t['team']['abbreviation'] == team['team']['abbreviation']), None)
                    
                    rankings[abbr] = {
                        'offensive_rank': overall_off_rank,
                        'defensive_rank': overall_def_rank,
                        'conference_offensive': conf_off_rank,
                        'conference_defensive': conf_def_rank,
                        'division_offensive': div_off_rank,
                        'division_defensive': div_def_rank
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
        """Get historical ranking data by fetching standings after each game"""
        historical = []
        
        try:
            from datetime import datetime, timedelta
            
            # Get team's game logs to find game dates
            api_abbr = self._convert_to_api_abbr(team_abbr)
            season = self._get_season(date)
            endpoint = f"{season}/team_gamelogs.json"
            params = {
                'team': api_abbr,
                'limit': num_games
            }
            url = f"{self.base_url}/{endpoint}"
            
            print(f"      Getting game dates for {team_abbr}...")
            time.sleep(self.request_delay)
            response = requests.get(url, auth=self.auth, params=params)
            
            if response.status_code == 429:
                time.sleep(self.retry_delay)
                response = requests.get(url, auth=self.auth, params=params)
            
            response.raise_for_status()
            game_data = response.json()
            
            if game_data and 'gamelogs' in game_data:
                games_chronological = list(reversed(game_data['gamelogs']))
                
                # print(f"      Fetching historical rankings for {len(games_chronological)} games...")
                
                for i, game in enumerate(games_chronological):
                    # Get standings after this game
                    game_date_str = game.get('game', {}).get('startTime', '')[:10]  # YYYY-MM-DD
                    
                    if i == len(games_chronological) - 1:
                        # Last game - use current standings
                        overall_standings = self._get_overall_standings(season)
                        stats_rankings = self._get_team_stats_rankings(season)
                    else:
                        # Fetch historical standings
                        formatted_date = game_date_str.replace('-', '')
                        
                        # Get standings as of that date
                        time.sleep(self.request_delay)
                        standings_url = f"{self.base_url}/{season}/standings.json?date={formatted_date}"
                        stats_url = f"{self.base_url}/{season}/team_stats_totals.json?date={formatted_date}"
                        
                        # Get overall standings for that date
                        standings_response = requests.get(standings_url, auth=self.auth)
                        if standings_response.status_code == 429:
                            time.sleep(self.retry_delay)
                            standings_response = requests.get(standings_url, auth=self.auth)
                        
                        overall_standings = {}
                        if standings_response.status_code == 200:
                            standings_data = standings_response.json()
                            if standings_data and 'teams' in standings_data:
                                teams_sorted = sorted(standings_data['teams'], 
                                                    key=lambda x: x['stats']['standings']['winPct'], 
                                                    reverse=True)
                                for rank, team in enumerate(teams_sorted, 1):
                                    abbr = team['team']['abbreviation']
                                    if abbr == 'BRO':
                                        abbr = 'BKN'
                                    elif abbr == 'OKL':
                                        abbr = 'OKC'
                                    overall_standings[abbr] = {'overall_rank': rank}
                        
                        # Get team stats for that date
                        time.sleep(self.request_delay)
                        stats_response = requests.get(stats_url, auth=self.auth)
                        if stats_response.status_code == 429:
                            time.sleep(self.retry_delay)
                            stats_response = requests.get(stats_url, auth=self.auth)
                        
                        stats_rankings = {}
                        if stats_response.status_code == 200:
                            stats_data = stats_response.json()
                            if stats_data and 'teamStatsTotals' in stats_data:
                                all_teams = stats_data['teamStatsTotals']
                                teams_off = sorted(all_teams, key=lambda x: x['stats']['offense']['ptsPerGame'], reverse=True)
                                teams_def = sorted(all_teams, key=lambda x: x['stats']['defense'].get('oppPtsPerGame', x['stats']['defense'].get('ptsAgainstPerGame', 0)))
                                
                                for team in all_teams:
                                    abbr = team['team']['abbreviation']
                                    if abbr == 'BRO':
                                        abbr = 'BKN'
                                    elif abbr == 'OKL':
                                        abbr = 'OKC'
                                    
                                    off_rank = next((idx for idx, t in enumerate(teams_off, 1) if t['team']['abbreviation'] == team['team']['abbreviation']), 15)
                                    def_rank = next((idx for idx, t in enumerate(teams_def, 1) if t['team']['abbreviation'] == team['team']['abbreviation']), 15)
                                    
                                    stats_rankings[abbr] = {
                                        'offensive_rank': off_rank,
                                        'defensive_rank': def_rank
                                    }
                    
                    # Extract rankings for this team
                    overall_rank = overall_standings.get(team_abbr, {}).get('overall_rank', 15)
                    offensive_rank = stats_rankings.get(team_abbr, {}).get('offensive_rank', 15)
                    defensive_rank = stats_rankings.get(team_abbr, {}).get('defensive_rank', 15)
                    
                    historical.append({
                        'game_num': i + 1,
                        'overall_rank': overall_rank,
                        'offensive_rank': offensive_rank,
                        'defensive_rank': defensive_rank
                    })
                    
                    print(f"        Game {i+1}/{len(games_chronological)}: Overall={overall_rank}, Off={offensive_rank}, Def={defensive_rank}")
            
            return historical if historical else [{'game_num': i+1, 'overall_rank': 15, 'offensive_rank': 15, 'defensive_rank': 15} for i in range(num_games)]
            
        except Exception as e:
            print(f"      Error fetching historical rankings: {e}")
            return [{'game_num': i+1, 'overall_rank': 15, 'offensive_rank': 15, 'defensive_rank': 15} for i in range(num_games)]
    
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
        print(f"    Getting overall standings...")
        overall_rankings = self._get_overall_standings(season)
        
        # Get offensive/defensive rankings
        print(f"    Getting team stats rankings...")
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
                'conference_offensive': away_rankings.get('conference_offensive', '-'),
                'conference_defensive': away_rankings.get('conference_defensive', '-'),
                'division_offensive': away_rankings.get('division_offensive', '-'),
                'division_defensive': away_rankings.get('division_defensive', '-'),
                'historical': away_historical
            },
            'home_rankings': {
                'overall': home_rankings.get('overall_rank', '-'),
                'offensive': home_rankings.get('offensive_rank', '-'),
                'defensive': home_rankings.get('defensive_rank', '-'),
                'conference': home_rankings.get('conference_rank', '-'),
                'division': home_rankings.get('division_rank', '-'),
                'conference_offensive': home_rankings.get('conference_offensive', '-'),
                'conference_defensive': home_rankings.get('conference_defensive', '-'),
                'division_offensive': home_rankings.get('division_offensive', '-'),
                'division_defensive': home_rankings.get('division_defensive', '-'),
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