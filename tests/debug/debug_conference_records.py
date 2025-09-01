#!/usr/bin/env python3
"""
Debug script to understand why conference/division records are incorrect
"""

import os
import json
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def debug_team_records(team='PHI', season='2024-2025-regular'):
    """Debug conference and division record calculations"""
    
    api_key = os.getenv('MSF_API_KEY')
    password = os.getenv('MSF_PASSWORD', 'MYSPORTSFEEDS')
    auth = HTTPBasicAuth(api_key, password)
    
    # Team conference/division info
    team_info = {
        'PHI': {'conf': 'Eastern', 'div': 'Atlantic'},
        'MIL': {'conf': 'Eastern', 'div': 'Central'}
    }
    
    # Eastern Conference teams
    eastern_teams = ['ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DET', 'IND', 
                     'MIA', 'MIL', 'NYK', 'ORL', 'PHI', 'TOR', 'WAS']
    
    # Atlantic Division teams
    atlantic_teams = ['BOS', 'BKN', 'NYK', 'PHI', 'TOR']
    
    # Central Division teams  
    central_teams = ['CHI', 'CLE', 'DET', 'IND', 'MIL']
    
    print(f"Debugging {team} records for {season}")
    print("=" * 60)
    
    # Get all games for the team
    url = f"https://api.mysportsfeeds.com/v2.1/pull/nba/{season}/games.json"
    params = {'team': team}
    
    try:
        response = requests.get(url, auth=auth, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Save raw response
        with open(f'cache/debug_{team}_games.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        overall_wins = 0
        overall_losses = 0
        conf_wins = 0
        conf_losses = 0
        div_wins = 0
        div_losses = 0
        
        games_analyzed = []
        
        if 'games' in data:
            for game in data['games']:
                schedule = game.get('schedule', {})
                score = game.get('score', {})
                
                # Get game details
                game_id = schedule.get('id', '')
                away_team = schedule.get('awayTeam', {}).get('abbreviation')
                home_team = schedule.get('homeTeam', {}).get('abbreviation')
                played_status = schedule.get('playedStatus', '')
                
                # Skip if not completed
                if played_status != 'COMPLETED' or not score:
                    continue
                
                # Determine opponent and whether team won
                if away_team == team:
                    opponent = home_team
                    team_score = score.get('awayScoreTotal', 0)
                    opp_score = score.get('homeScoreTotal', 0)
                    location = 'Away'
                elif home_team == team:
                    opponent = away_team
                    team_score = score.get('homeScoreTotal', 0)
                    opp_score = score.get('awayScoreTotal', 0)
                    location = 'Home'
                else:
                    continue  # Team not in this game
                
                won = team_score > opp_score
                
                # Count overall
                if won:
                    overall_wins += 1
                else:
                    overall_losses += 1
                
                # Check conference
                is_conf_game = opponent in eastern_teams if team in eastern_teams else opponent not in eastern_teams
                
                # Check division
                is_div_game = False
                if team in atlantic_teams and opponent in atlantic_teams:
                    is_div_game = True
                elif team in central_teams and opponent in central_teams:
                    is_div_game = True
                
                # Count conference games
                if is_conf_game:
                    if won:
                        conf_wins += 1
                    else:
                        conf_losses += 1
                
                # Count division games
                if is_div_game:
                    if won:
                        div_wins += 1
                    else:
                        div_losses += 1
                
                # Store game info for analysis
                games_analyzed.append({
                    'game_id': game_id,
                    'opponent': opponent,
                    'location': location,
                    'score': f"{team_score}-{opp_score}",
                    'won': won,
                    'is_conf': is_conf_game,
                    'is_div': is_div_game
                })
        
        # Display results
        print(f"\n{team} RECORD ANALYSIS")
        print("-" * 40)
        print(f"Overall: {overall_wins}-{overall_losses}")
        print(f"Conference: {conf_wins}-{conf_losses}")
        print(f"Division: {div_wins}-{div_losses}")
        
        print(f"\nTotal games analyzed: {len(games_analyzed)}")
        
        # Show conference games
        print(f"\nCONFERENCE GAMES ({conf_wins + conf_losses} total):")
        print("-" * 40)
        conf_games = [g for g in games_analyzed if g['is_conf']]
        for g in conf_games[:10]:  # Show first 10
            result = "W" if g['won'] else "L"
            print(f"{result} vs {g['opponent']} ({g['score']}) - {g['location']}")
        if len(conf_games) > 10:
            print(f"... and {len(conf_games) - 10} more conference games")
        
        # Show division games
        print(f"\nDIVISION GAMES ({div_wins + div_losses} total):")
        print("-" * 40)
        div_games = [g for g in games_analyzed if g['is_div']]
        for g in div_games:
            result = "W" if g['won'] else "L"
            print(f"{result} vs {g['opponent']} ({g['score']}) - {g['location']}")
        
        # Check for issues
        print("\nPOTENTIAL ISSUES CHECK:")
        print("-" * 40)
        
        # Check if all Eastern teams are being recognized
        eastern_opponents = [g['opponent'] for g in games_analyzed if g['opponent'] in eastern_teams]
        print(f"Games vs Eastern teams: {len(eastern_opponents)}")
        print(f"Unique Eastern opponents: {set(eastern_opponents)}")
        
        # Check division opponents
        if team in atlantic_teams:
            div_opponents = [g['opponent'] for g in games_analyzed if g['opponent'] in atlantic_teams and g['opponent'] != team]
            print(f"Games vs Atlantic teams: {len(div_opponents)}")
            print(f"Atlantic opponents faced: {set(div_opponents)}")
        
        # Save detailed analysis
        analysis_file = f'cache/debug_{team}_analysis.json'
        with open(analysis_file, 'w') as f:
            json.dump({
                'team': team,
                'season': season,
                'records': {
                    'overall': f"{overall_wins}-{overall_losses}",
                    'conference': f"{conf_wins}-{conf_losses}",
                    'division': f"{div_wins}-{div_losses}"
                },
                'games': games_analyzed
            }, f, indent=2)
        
        print(f"\nDetailed analysis saved to: {analysis_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text[:500]}")

if __name__ == "__main__":
    from pathlib import Path
    Path("cache").mkdir(exist_ok=True)
    
    # Debug PHI first (the problematic one)
    debug_team_records('PHI', '2024-2025-regular')
    
    print("\n" + "="*60 + "\n")
    
    # Then debug MIL for comparison
    debug_team_records('MIL', '2024-2025-regular')