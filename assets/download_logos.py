#!/usr/bin/env python3
"""
Simple script to download NBA team logos
Run this once to get all team logos for your reports
"""

import os
import requests
from pathlib import Path
import time

def download_nba_logos():
    """Download all NBA team logos from ESPN CDN"""
    
    # Create directory
    logo_dir = Path('assets/teams')
    logo_dir.mkdir(parents=True, exist_ok=True)
    
    # All 30 NBA teams
    teams = [
        'ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW',
        'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK',
        'OKC', 'ORL', 'PHI', 'PHX', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS'
    ]
    
    print("Downloading NBA Team Logos")
    print("=" * 40)
    
    success_count = 0
    fail_count = 0
    
    for team in teams:
        # ESPN CDN URL - reliable and good quality
        url = f'https://a.espncdn.com/i/teamlogos/nba/500/{team.lower()}.png'
        output_path = logo_dir / f'{team}.png'
        
        # Skip if already exists
        if output_path.exists():
            print(f"✓ {team}: Already exists")
            success_count += 1
            continue
        
        try:
            print(f"  Downloading {team}...", end='')
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f" ✓")
                success_count += 1
            else:
                print(f" ✗ (Status: {response.status_code})")
                fail_count += 1
                
        except Exception as e:
            print(f" ✗ (Error: {str(e)[:30]})")
            fail_count += 1
        
        # Be nice to the server
        time.sleep(0.5)
    
    print("\n" + "=" * 40)
    print(f"Complete! Downloaded: {success_count}/{len(teams)}")
    if fail_count > 0:
        print(f"Failed: {fail_count}")
    print(f"Logos saved to: {logo_dir.absolute()}")
    
    return success_count, fail_count

if __name__ == "__main__":
    download_nba_logos()