#!/usr/bin/env python3
"""
Verify that conference and division games add up correctly
Should total 82 games for a complete season
"""

import os
import json
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from collections import defaultdict, Counter

load_dotenv()

class GameVerifier:
    def __init__(self):
        self.api_key = os.getenv('MSF_API_KEY')
        self.password = os.getenv('MSF_PASSWORD', 'MYSPORTSFEEDS')
        self.auth = HTTPBasicAuth(self.api_key, self.password)
        self.base_url = 'https://api.mysportsfeeds.com/v2.1/pull/nba'
        
        # Conference assignments (with API abbreviations)
        self.eastern_teams = ['ATL', 'BOS', 'BRO', 'CHA', 'CHI', 'CLE', 'DET', 'IND', 
                             'MIA', 'MIL', 'NYK', 'ORL', 'PHI', 'TOR', 'WAS']
        
        self.western_teams = ['DAL', 'DEN', 'GSW', 'HOU', 'LAC', 'LAL', 'MEM', 'MIN',
                             'NOP', 'OKL', 'PHX', 'POR', 'SAC', 'SAS', 'UTA']
        
        # Division assignments (with API abbreviations)
        self.divisions = {
            'Atlantic': ['BOS', 'BRO', 'NYK', 'PHI', 'TOR'],
            'Central': ['CHI', 'CLE', 'DET', 'IND', 'MIL'],
            'Southeast': ['ATL', 'CHA', 'MIA', 'ORL', 'WAS'],
            'Southwest': ['DAL', 'HOU', 'MEM', 'NOP', 'SAS'],
            'Northwest': ['DEN', 'MIN', 'OKL', 'POR', 'UTA'],
            'Pacific': ['GSW', 'LAC', 'LAL', 'PHX', 'SAC']
        }
        
        # Reverse mapping for easy lookup
        self.team_division = {}
        for div, teams in self.divisions.items():
            for team in teams:
                self.team_division[team] = div
    
    def verify_team_games(self, team='PHI', season='2024-2025-regular'):
        """Verify all game categorizations for a team"""
        
        print(f"\nVerifying {team} games for {season}")
        print("="*70)
        
        # Get all games
        url = f"{self.base_url}/{season}/games.json"
        params = {'team': team}
        
        try:
            response = requests.get(url, auth=self.auth, params=params)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Error fetching games: {e}")
            return
        
        # Categorize games
        results = {
            'vs_own_division': {'wins': 0, 'losses': 0, 'opponents': []},
            'vs_own_conf_other_div': {'wins': 0, 'losses': 0, 'opponents': []},
            'vs_other_conf': {'wins': 0, 'losses': 0, 'opponents': []},
            'total': {'wins': 0, 'losses': 0}
        }
        
        team_conf = 'Eastern' if team in self.eastern_teams else 'Western'
        team_div = self.team_division.get(team)
        
        games_by_opponent = defaultdict(list)
        
        if 'games' in data:
            for game in data['games']:
                schedule = game.get('schedule', {})
                score = game.get('score', {})
                
                # Skip incomplete games
                if schedule.get('playedStatus') != 'COMPLETED' or not score:
                    continue
                
                # Determine opponent and result
                away_team = schedule.get('awayTeam', {}).get('abbreviation')
                home_team = schedule.get('homeTeam', {}).get('abbreviation')
                away_score = score.get('awayScoreTotal', 0)
                home_score = score.get('homeScoreTotal', 0)
                
                if away_team == team:
                    opponent = home_team
                    won = away_score > home_score
                    location = '@'
                elif home_team == team:
                    opponent = away_team
                    won = home_score > away_score
                    location = 'vs'
                else:
                    continue
                
                # Store game info
                game_info = {
                    'opponent': opponent,
                    'location': location,
                    'won': won,
                    'score': f"{max(away_score, home_score)}-{min(away_score, home_score)}"
                }
                games_by_opponent[opponent].append(game_info)
                
                # Categorize game
                opp_conf = 'Eastern' if opponent in self.eastern_teams else 'Western'
                opp_div = self.team_division.get(opponent)
                
                # Update totals
                if won:
                    results['total']['wins'] += 1
                else:
                    results['total']['losses'] += 1
                
                # Categorize by opponent type
                if opp_div == team_div:
                    # Same division
                    category = 'vs_own_division'
                elif opp_conf == team_conf:
                    # Same conference, different division
                    category = 'vs_own_conf_other_div'
                else:
                    # Different conference
                    category = 'vs_other_conf'
                
                if won:
                    results[category]['wins'] += 1
                else:
                    results[category]['losses'] += 1
                results[category]['opponents'].append(opponent)
        
        # Display results
        total_games = results['total']['wins'] + results['total']['losses']
        
        print(f"\n{team} COMPLETE SEASON BREAKDOWN")
        print("-"*70)
        print(f"Overall Record: {results['total']['wins']}-{results['total']['losses']} ({total_games} games)")
        
        # Division games
        div_games = results['vs_own_division']
        div_total = div_games['wins'] + div_games['losses']
        print(f"\nvs. Own Division ({team_div}):")
        print(f"  Record: {div_games['wins']}-{div_games['losses']} ({div_total} games)")
        div_opponents = Counter(div_games['opponents'])
        for opp, count in sorted(div_opponents.items()):
            print(f"    vs {opp}: {count} games")
        
        # Conference games (other divisions)
        conf_other = results['vs_own_conf_other_div']
        conf_other_total = conf_other['wins'] + conf_other['losses']
        print(f"\nvs. {team_conf} Conference (other divisions):")
        print(f"  Record: {conf_other['wins']}-{conf_other['losses']} ({conf_other_total} games)")
        
        # Show by division
        conf_by_div = defaultdict(list)
        for opp in conf_other['opponents']:
            opp_div = self.team_division.get(opp)
            conf_by_div[opp_div].append(opp)
        
        for div, opps in sorted(conf_by_div.items()):
            opp_counts = Counter(opps)
            print(f"  vs {div} Division: {len(opps)} games")
            for opp, count in sorted(opp_counts.items()):
                print(f"    vs {opp}: {count} games")
        
        # Inter-conference games
        inter_conf = results['vs_other_conf']
        inter_total = inter_conf['wins'] + inter_conf['losses']
        print(f"\nvs. {('Western' if team_conf == 'Eastern' else 'Eastern')} Conference:")
        print(f"  Record: {inter_conf['wins']}-{inter_conf['losses']} ({inter_total} games)")
        
        # Show by division
        inter_by_div = defaultdict(list)
        for opp in inter_conf['opponents']:
            opp_div = self.team_division.get(opp)
            inter_by_div[opp_div].append(opp)
        
        for div, opps in sorted(inter_by_div.items()):
            opp_counts = Counter(opps)
            print(f"  vs {div} Division: {len(opps)} games")
            for opp, count in sorted(opp_counts.items()):
                print(f"    vs {opp}: {count} games")
        
        # Summary
        print("\n" + "="*70)
        print("VERIFICATION SUMMARY")
        print("-"*70)
        
        # Total conference games
        total_conf_games = div_total + conf_other_total
        conf_record_wins = div_games['wins'] + conf_other['wins']
        conf_record_losses = div_games['losses'] + conf_other['losses']
        
        print(f"Total Games: {total_games} (should be 82)")
        print(f"Conference Record: {conf_record_wins}-{conf_record_losses} ({total_conf_games} games)")
        print(f"Division Record: {div_games['wins']}-{div_games['losses']} ({div_total} games)")
        print(f"Inter-Conference: {inter_conf['wins']}-{inter_conf['losses']} ({inter_total} games)")
        
        # Verify totals
        print("\nVERIFICATION CHECKS:")
        print(f"✓ Total = Division + Conf(other) + Inter-conf: {total_games} = {div_total} + {conf_other_total} + {inter_total}")
        print(f"✓ Conference games = Division + Conf(other): {total_conf_games} = {div_total} + {conf_other_total}")
        
        if total_games == 82:
            print("✅ Total games equals 82 - VERIFIED!")
        else:
            print(f"⚠️  Total games is {total_games}, not 82")
        
        # Save detailed breakdown
        output_file = f'cache/{team}_game_breakdown.json'
        with open(output_file, 'w') as f:
            json.dump({
                'team': team,
                'season': season,
                'total_games': total_games,
                'overall_record': f"{results['total']['wins']}-{results['total']['losses']}",
                'conference_record': f"{conf_record_wins}-{conf_record_losses}",
                'division_record': f"{div_games['wins']}-{div_games['losses']}",
                'breakdown': results,
                'games_by_opponent': {k: v for k, v in games_by_opponent.items()}
            }, f, indent=2)
        
        print(f"\nDetailed breakdown saved to: {output_file}")
        
        return results

if __name__ == "__main__":
    from pathlib import Path
    Path("cache").mkdir(exist_ok=True)
    
    verifier = GameVerifier()
    
    # Verify PHI first
    phi_results = verifier.verify_team_games('PHI', '2024-2025-regular')
    
    # Then verify MIL
    mil_results = verifier.verify_team_games('MIL', '2024-2025-regular')