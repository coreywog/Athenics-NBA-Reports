#!/usr/bin/env python3
"""
Team Stats Collector - Fixed with Better Rate Limiting
Reduces 429 errors by adding proper delays and retry logic
"""

import os
import requests
from typing import Dict, Optional
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import time

load_dotenv()

class TeamStatsCollector:
    """Collects comprehensive team statistics for the matchup report"""
    
    def __init__(self):
        self.api_key = os.getenv('MSF_API_KEY')
        self.password = os.getenv('MSF_PASSWORD', 'MYSPORTSFEEDS')
        self.base_url = 'https://api.mysportsfeeds.com/v2.1/pull/nba'
        self.auth = HTTPBasicAuth(self.api_key, self.password)
        
        # Rate limiting settings - INCREASED DELAYS
        self.request_delay = 2.0  # Increased from 1 to 2 seconds between requests
        self.retry_delay = 20  # 20 seconds on rate limit as requested
        
        # API to common abbreviation mapping
        self.api_to_common = {
            'BRO': 'BKN',  # Brooklyn Nets
            'OKL': 'OKC',  # Oklahoma City Thunder
        }
        
        # Common to API abbreviation mapping
        self.common_to_api = {
            'BKN': 'BRO',  # Brooklyn Nets
            'OKC': 'OKL',  # Oklahoma City Thunder
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
        """Make API request with proper rate limiting and retry logic"""
        url = f"{self.base_url}/{endpoint}"
        
        # ALWAYS delay before making a request
        time.sleep(self.request_delay)
        
        try:
            response = requests.get(url, auth=self.auth, params=params)
            
            # Handle rate limiting
            if response.status_code == 429:
                print(f"  ⚠️  Rate limited on {endpoint}. Waiting {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
                # Try one more time after waiting
                response = requests.get(url, auth=self.auth, params=params)
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"  ❌ Error fetching {endpoint}: {e}")
            return None
    
    def get_team_season_stats(self, team: str, season: str) -> Dict:
        """Get comprehensive season statistics for a team using team_stats_totals endpoint"""
        endpoint = f"{season}/team_stats_totals.json"
        params = {'team': team}
        
        data = self._make_request(endpoint, params)
        
        stats = {
            'offensive': {},
            'defensive': {},
            'other': {}
        }
        
        if data and 'teamStatsTotals' in data:
            for team_data in data['teamStatsTotals']:
                if team_data.get('team', {}).get('abbreviation') == team:
                    team_stats = team_data.get('stats', {})
                    
                    # Get games played
                    games_played = team_stats.get('gamesPlayed', 1) or 1
                    
                    # Field Goals
                    field_goals = team_stats.get('fieldGoals', {})
                    
                    # Free Throws
                    free_throws = team_stats.get('freeThrows', {})
                    
                    # Rebounds
                    rebounds = team_stats.get('rebounds', {})
                    
                    # Offense
                    offense = team_stats.get('offense', {})
                    
                    # Defense
                    defense = team_stats.get('defense', {})
                    
                    # Standings
                    standings = team_stats.get('standings', {})
                    
                    # Offensive Stats
                    stats['offensive'] = {
                        'ppg': round(offense.get('ptsPerGame', 0), 1),
                        'fg_made': round(field_goals.get('fgMadePerGame', 0), 1),
                        'fg_att': round(field_goals.get('fgAttPerGame', 0), 1),
                        'fg_pct': round(field_goals.get('fgPct', 0), 1),
                        'three_made': round(field_goals.get('fg3PtMadePerGame', 0), 1),
                        'three_att': round(field_goals.get('fg3PtAttPerGame', 0), 1),
                        'three_pct': round(field_goals.get('fg3PtPct', 0), 1),
                        'ft_made': round(free_throws.get('ftMadePerGame', 0), 1),
                        'ft_att': round(free_throws.get('ftAttPerGame', 0), 1),
                        'ft_pct': round(free_throws.get('ftPct', 0), 1),
                        'ast': round(offense.get('astPerGame', 0), 1),
                        'turnovers': round(defense.get('tovPerGame', 0), 1)
                    }
                    
                    # Defensive/Rebounding Stats
                    stats['defensive'] = {
                        'reb': round(rebounds.get('rebPerGame', 0), 1),
                        'off_reb': round(rebounds.get('offRebPerGame', 0), 1),
                        'def_reb': round(rebounds.get('defRebPerGame', 0), 1),
                        'stl': round(defense.get('stlPerGame', 0), 1),
                        'blk': round(defense.get('blkPerGame', 0), 1),
                        'opp_ppg': round(defense.get('ptsAgainstPerGame', 0), 1),
                        'fouls': round(team_stats.get('miscellaneous', {}).get('foulsPerGame', 0), 1)
                    }
                    
                    # Other Stats
                    stats['other'] = {
                        'games_played': games_played,
                        'wins': standings.get('wins', 0),
                        'losses': standings.get('losses', 0),
                        'win_pct': round(standings.get('winPct', 0), 3),
                        'points_for': round(offense.get('ptsPerGame', 0), 1),
                        'points_against': round(defense.get('ptsAgainstPerGame', 0), 1)
                    }
                    
                    break
        
        return stats
    
    def get_standings_info(self, team: str, season: str) -> Dict:
        """Get team standings information including rankings"""
        endpoint = f"{season}/standings.json"
        params = {'team': team}
        
        data = self._make_request(endpoint, params)
        
        rankings = {}
        
        if data and 'teams' in data:
            for team_data in data['teams']:
                if team_data.get('team', {}).get('abbreviation') == team:
                    rankings = {
                        'overall_rank': team_data.get('overallRank', {}).get('rank', 0),
                        'conference_rank': team_data.get('conferenceRank', {}).get('rank', 0),
                        'division_rank': team_data.get('divisionRank', {}).get('rank', 0),
                        'playoff_rank': team_data.get('playoffRank', {}).get('rank', 0)
                    }
                    break
        
        return rankings
    
    def get_recent_form_stats(self, team: str, season: str, last_n_games: int = 5) -> Dict:
        """Get stats from last N games - SIMPLIFIED to avoid too many API calls"""
        # Skip this for now to reduce API calls
        # You can re-enable this later if needed
        print(f"  ⏭️  Skipping recent form to reduce API calls")
        
        return {
            'last_n': last_n_games,
            'record': 'N/A',
            'ppg': 0,
            'opp_ppg': 0,
            'avg_margin': 0
        }
    
    def collect(self, away_team: str, home_team: str, date: str) -> Dict:
        """
        Collect all team statistics for both teams with better rate limiting
        
        Args:
            away_team: Away team abbreviation
            home_team: Home team abbreviation
            date: Date in YYYYMMDD format
            
        Returns:
            Dictionary with comprehensive team statistics
        """
        # Convert to API abbreviations
        away_api = self._convert_to_api_abbr(away_team)
        home_api = self._convert_to_api_abbr(home_team)
        
        # Convert to common abbreviations for display
        away_common = self._convert_to_common_abbr(away_api)
        home_common = self._convert_to_common_abbr(home_api)
        
        print(f"\n📊 Collecting team statistics for {away_common} @ {home_common}")
        print(f"  (Using {self.request_delay}s delay between API calls)")
        
        season = self._get_season(date)
        
        # Get season stats for both teams
        print("  • Fetching away team season statistics...")
        away_stats = self.get_team_season_stats(away_api, season)
        
        print("  • Fetching home team season statistics...")
        home_stats = self.get_team_season_stats(home_api, season)
        
        # Get standings/rankings - COMBINED CALL
        print("  • Fetching standings for both teams...")
        # Make a single call without team parameter to get all standings
        endpoint = f"{season}/standings.json"
        all_standings_data = self._make_request(endpoint, {})
        
        away_rankings = {}
        home_rankings = {}
        
        if all_standings_data and 'teams' in all_standings_data:
            for team_data in all_standings_data['teams']:
                team_abbr = team_data.get('team', {}).get('abbreviation')
                if team_abbr == away_api:
                    away_rankings = {
                        'overall_rank': team_data.get('overallRank', {}).get('rank', 0),
                        'conference_rank': team_data.get('conferenceRank', {}).get('rank', 0),
                        'division_rank': team_data.get('divisionRank', {}).get('rank', 0),
                        'playoff_rank': team_data.get('playoffRank', {}).get('rank', 0)
                    }
                elif team_abbr == home_api:
                    home_rankings = {
                        'overall_rank': team_data.get('overallRank', {}).get('rank', 0),
                        'conference_rank': team_data.get('conferenceRank', {}).get('rank', 0),
                        'division_rank': team_data.get('divisionRank', {}).get('rank', 0),
                        'playoff_rank': team_data.get('playoffRank', {}).get('rank', 0)
                    }
                
                # Stop if we found both teams
                if away_rankings and home_rankings:
                    break
        
        # Skip recent form to reduce API calls
        away_recent = {
            'last_n': 5,
            'record': 'N/A',
            'ppg': 0,
            'opp_ppg': 0,
            'avg_margin': 0
        }
        home_recent = {
            'last_n': 5,
            'record': 'N/A',
            'ppg': 0,
            'opp_ppg': 0,
            'avg_margin': 0
        }
        
        print("  ✅ Team statistics collection complete!")
        
        # Combine all stats
        away_combined = {
            **away_stats,
            'rankings': away_rankings,
            'recent_form': away_recent,
            'opponent_stats': {
                'opp_ppg': away_stats.get('defensive', {}).get('opp_ppg', 0),
                'opp_fg_pct': 0,
                'opp_three_pct': 0,
                'opp_reb': 0,
                'opp_ast': 0,
                'opp_turnovers': 0
            }
        }
        
        home_combined = {
            **home_stats,
            'rankings': home_rankings,
            'recent_form': home_recent,
            'opponent_stats': {
                'opp_ppg': home_stats.get('defensive', {}).get('opp_ppg', 0),
                'opp_fg_pct': 0,
                'opp_three_pct': 0,
                'opp_reb': 0,
                'opp_ast': 0,
                'opp_turnovers': 0
            }
        }
        
        return {
            'away_team_stats': away_combined,
            'home_team_stats': home_combined,
            'comparison': self._generate_comparison(away_combined, home_combined)
        }
    
    def _generate_comparison(self, away_stats: Dict, home_stats: Dict) -> Dict:
        """Generate statistical comparisons between teams"""
        comparison = {}
        
        # Offensive comparison
        if away_stats.get('offensive') and home_stats.get('offensive'):
            away_off = away_stats['offensive']
            home_off = home_stats['offensive']
            
            comparison['offensive'] = {
                'ppg_diff': round(away_off['ppg'] - home_off['ppg'], 1),
                'fg_pct_diff': round(away_off['fg_pct'] - home_off['fg_pct'], 1),
                'three_pct_diff': round(away_off['three_pct'] - home_off['three_pct'], 1),
                'ast_diff': round(away_off['ast'] - home_off['ast'], 1)
            }
        
        # Defensive comparison
        if away_stats.get('defensive') and home_stats.get('defensive'):
            away_def = away_stats['defensive']
            home_def = home_stats['defensive']
            
            comparison['defensive'] = {
                'reb_diff': round(away_def['reb'] - home_def['reb'], 1),
                'stl_diff': round(away_def['stl'] - home_def['stl'], 1),
                'blk_diff': round(away_def['blk'] - home_def['blk'], 1),
                'opp_ppg_diff': round(away_def['opp_ppg'] - home_def['opp_ppg'], 1)
            }
        
        # Recent form comparison
        if away_stats.get('recent_form') and home_stats.get('recent_form'):
            away_recent = away_stats['recent_form']
            home_recent = home_stats['recent_form']
            
            comparison['recent'] = {
                'ppg_diff': round(away_recent['ppg'] - home_recent['ppg'], 1) if away_recent['ppg'] else 0,
                'margin_diff': round(away_recent['avg_margin'] - home_recent['avg_margin'], 1) if away_recent['avg_margin'] else 0
            }
        
        # Rankings comparison
        if away_stats.get('rankings') and home_stats.get('rankings'):
            away_rank = away_stats['rankings']
            home_rank = home_stats['rankings']
            
            comparison['rankings'] = {
                'overall_rank_diff': away_rank.get('overall_rank', 0) - home_rank.get('overall_rank', 0),
                'conference_rank_diff': away_rank.get('conference_rank', 0) - home_rank.get('conference_rank', 0),
                'playoff_rank_diff': away_rank.get('playoff_rank', 0) - home_rank.get('playoff_rank', 0)
            }
        
        return comparison


# Test the collector
if __name__ == "__main__":
    collector = TeamStatsCollector()
    
    # Test with sample teams
    data = collector.collect('MIL', 'PHI', '20250119')
    
    import json
    print("\nTeam Statistics Data:")
    print("=" * 60)
    print(json.dumps(data, indent=2))