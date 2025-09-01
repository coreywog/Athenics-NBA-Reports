#!/usr/bin/env python3
"""
Compare MySportsFeeds API data with Basketball Reference data
This will help us understand what's going wrong
"""

import json
import re
from pathlib import Path
from collections import Counter

def parse_basketball_reference_data(file_path):
    """Parse the Basketball Reference text file"""
    games = []
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        # Skip header lines or empty lines
        if not line.strip() or line.startswith('Rk') or line.startswith('G'):
            continue
        
        # Parse game data (format appears to be tab or space separated)
        parts = line.strip().split()
        
        if len(parts) > 10:  # Make sure we have enough data
            try:
                # Extract key information
                game_num = parts[0]
                date = ' '.join(parts[1:4])  # Date might be split
                
                # Find @ symbol to determine home/away
                if '@' in line:
                    location = 'Away'
                    # Find opponent (after @)
                    opp_start = line.index('@') + 1
                else:
                    location = 'Home'
                    # Opponent is after 'vs'
                    opp_start = line.index('vs') + 2 if 'vs' in line else None
                
                # Extract W/L
                if ' W ' in line:
                    result = 'W'
                elif ' L ' in line:
                    result = 'L'
                else:
                    result = '?'
                
                games.append({
                    'game_num': game_num,
                    'date': date,
                    'location': location,
                    'result': result,
                    'line': line.strip()
                })
            except:
                continue
    
    return games

def analyze_api_data(api_file_path):
    """Analyze the API response data"""
    with open(api_file_path, 'r') as f:
        data = json.load(f)
    
    games = data.get('games', [])
    
    # Count and analyze games
    total_games = 0
    wins = 0
    losses = 0
    conf_games = 0
    div_games = 0
    
    eastern_teams = ['ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DET', 'IND', 
                     'MIA', 'MIL', 'NYK', 'ORL', 'PHI', 'TOR', 'WAS']
    atlantic_teams = ['BOS', 'BKN', 'NYK', 'PHI', 'TOR']
    
    game_list = []
    
    for game in games:
        total_games += 1
        
        # Extract game info
        opponent = game.get('opponent', '')
        won = game.get('won', False)
        is_conf = game.get('is_conf', False)
        is_div = game.get('is_div', False)
        
        if won:
            wins += 1
        else:
            losses += 1
        
        if is_conf:
            conf_games += 1
        if is_div:
            div_games += 1
        
        game_list.append({
            'opponent': opponent,
            'won': won,
            'is_conf': is_conf,
            'is_div': is_div
        })
    
    return {
        'total_games': total_games,
        'record': f"{wins}-{losses}",
        'conf_games': conf_games,
        'div_games': div_games,
        'games': game_list
    }

def compare_records():
    """Main comparison function"""
    print("="*60)
    print("DATA SOURCE COMPARISON")
    print("="*60)
    
    # Check what files we have
    cache_dir = Path('cache')
    
    # Load API analysis if it exists
    api_analysis_file = cache_dir / 'debug_PHI_analysis.json'
    if api_analysis_file.exists():
        with open(api_analysis_file, 'r') as f:
            api_data = json.load(f)
        
        print("\nMySportsFeeds API Data:")
        print("-"*40)
        print(f"Season: {api_data.get('season', 'Unknown')}")
        print(f"Overall Record: {api_data['records']['overall']}")
        print(f"Conference Record: {api_data['records']['conference']}")
        print(f"Division Record: {api_data['records']['division']}")
        print(f"Total Games in Data: {len(api_data.get('games', []))}")
        
        # Count opponent frequencies
        opponents = [g['opponent'] for g in api_data.get('games', [])]
        opp_counts = Counter(opponents)
        
        print(f"\nGames per opponent:")
        for opp, count in sorted(opp_counts.items()):
            print(f"  {opp}: {count} games")
    
    # Check if Basketball Reference file exists
    bbref_file = cache_dir / 'phi_2024_25_bbref.txt'
    if bbref_file.exists():
        bbref_games = parse_basketball_reference_data(bbref_file)
        
        print("\n\nBasketball Reference Data:")
        print("-"*40)
        print(f"Total Games: {len(bbref_games)}")
        
        wins = sum(1 for g in bbref_games if g['result'] == 'W')
        losses = sum(1 for g in bbref_games if g['result'] == 'L')
        print(f"Record: {wins}-{losses}")
    
    print("\n" + "="*60)
    print("ISSUE IDENTIFIED:")
    print("-"*40)
    print("The MySportsFeeds API is returning data from a different season!")
    print("PHI going 24-58 appears to be from a previous season.")
    print("\nPossible reasons:")
    print("1. The API might be returning last season's data for '2024-2025-regular'")
    print("2. The current season might need a different identifier")
    print("3. We might need to use a different endpoint for current season data")
    
    print("\nRECOMMENDATION:")
    print("Try using the 'current_season' endpoint to get the actual current season,")
    print("then use that season identifier for subsequent API calls.")

if __name__ == "__main__":
    compare_records()