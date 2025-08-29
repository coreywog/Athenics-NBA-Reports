"""
NBA Team Assets Manager
Handles team logos, colors, and branding assets
"""

import os
import requests
from pathlib import Path
from typing import Dict, Tuple
import json

class TeamAssetsManager:
    """Manage NBA team logos and brand colors"""
    
    def __init__(self):
        self.assets_dir = Path('assets/teams')
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        
        # Team configurations with colors and logo sources
        self.teams = {
            'ATL': {
                'name': 'Atlanta Hawks',
                'colors': {'primary': '#E03A3E', 'secondary': '#C1D32F', 'tertiary': '#26282A'},
                'abbreviation': 'ATL'
            },
            'BOS': {
                'name': 'Boston Celtics',
                'colors': {'primary': '#007A33', 'secondary': '#BA9653', 'tertiary': '#963821'},
                'abbreviation': 'BOS'
            },
            'BKN': {
                'name': 'Brooklyn Nets',
                'colors': {'primary': '#000000', 'secondary': '#FFFFFF', 'tertiary': '#777D84'},
                'abbreviation': 'BKN'
            },
            'CHA': {
                'name': 'Charlotte Hornets',
                'colors': {'primary': '#1D1160', 'secondary': '#00788C', 'tertiary': '#A1A1A4'},
                'abbreviation': 'CHA'
            },
            'CHI': {
                'name': 'Chicago Bulls',
                'colors': {'primary': '#CE1141', 'secondary': '#000000', 'tertiary': '#FFFFFF'},
                'abbreviation': 'CHI'
            },
            'CLE': {
                'name': 'Cleveland Cavaliers',
                'colors': {'primary': '#860038', 'secondary': '#041E42', 'tertiary': '#FDBB30'},
                'abbreviation': 'CLE'
            },
            'DAL': {
                'name': 'Dallas Mavericks',
                'colors': {'primary': '#00538C', 'secondary': '#002B5E', 'tertiary': '#B8C4CA'},
                'abbreviation': 'DAL'
            },
            'DEN': {
                'name': 'Denver Nuggets',
                'colors': {'primary': '#0E2240', 'secondary': '#FEC524', 'tertiary': '#8B2131'},
                'abbreviation': 'DEN'
            },
            'DET': {
                'name': 'Detroit Pistons',
                'colors': {'primary': '#C8102E', 'secondary': '#1D42BA', 'tertiary': '#BEC0C2'},
                'abbreviation': 'DET'
            },
            'GSW': {
                'name': 'Golden State Warriors',
                'colors': {'primary': '#1D428A', 'secondary': '#FFC72C', 'tertiary': '#FFFFFF'},
                'abbreviation': 'GSW'
            },
            'HOU': {
                'name': 'Houston Rockets',
                'colors': {'primary': '#CE1141', 'secondary': '#000000', 'tertiary': '#C4CED4'},
                'abbreviation': 'HOU'
            },
            'IND': {
                'name': 'Indiana Pacers',
                'colors': {'primary': '#002D62', 'secondary': '#FDBB30', 'tertiary': '#BEC0C2'},
                'abbreviation': 'IND'
            },
            'LAC': {
                'name': 'LA Clippers',
                'colors': {'primary': '#C8102E', 'secondary': '#1D428A', 'tertiary': '#BEC0C2'},
                'abbreviation': 'LAC'
            },
            'LAL': {
                'name': 'Los Angeles Lakers',
                'colors': {'primary': '#552583', 'secondary': '#FDB927', 'tertiary': '#000000'},
                'abbreviation': 'LAL'
            },
            'MEM': {
                'name': 'Memphis Grizzlies',
                'colors': {'primary': '#5D76A9', 'secondary': '#12173F', 'tertiary': '#F5B112'},
                'abbreviation': 'MEM'
            },
            'MIA': {
                'name': 'Miami Heat',
                'colors': {'primary': '#98002E', 'secondary': '#F9A01B', 'tertiary': '#000000'},
                'abbreviation': 'MIA'
            },
            'MIL': {
                'name': 'Milwaukee Bucks',
                'colors': {'primary': '#00471B', 'secondary': '#EEE1C6', 'tertiary': '#0077C0'},
                'abbreviation': 'MIL'
            },
            'MIN': {
                'name': 'Minnesota Timberwolves',
                'colors': {'primary': '#0C2340', 'secondary': '#236192', 'tertiary': '#9EA2A2'},
                'abbreviation': 'MIN'
            },
            'NOP': {
                'name': 'New Orleans Pelicans',
                'colors': {'primary': '#0C2340', 'secondary': '#C8102E', 'tertiary': '#85714D'},
                'abbreviation': 'NOP'
            },
            'NYK': {
                'name': 'New York Knicks',
                'colors': {'primary': '#006BB6', 'secondary': '#F58426', 'tertiary': '#BEC0C2'},
                'abbreviation': 'NYK'
            },
            'OKC': {
                'name': 'Oklahoma City Thunder',
                'colors': {'primary': '#007AC1', 'secondary': '#EF3B24', 'tertiary': '#002D62'},
                'abbreviation': 'OKC'
            },
            'ORL': {
                'name': 'Orlando Magic',
                'colors': {'primary': '#0077C0', 'secondary': '#C4CED4', 'tertiary': '#000000'},
                'abbreviation': 'ORL'
            },
            'PHI': {
                'name': 'Philadelphia 76ers',
                'colors': {'primary': '#006BB6', 'secondary': '#ED174C', 'tertiary': '#002B5C'},
                'abbreviation': 'PHI'
            },
            'PHX': {
                'name': 'Phoenix Suns',
                'colors': {'primary': '#1D1160', 'secondary': '#E56020', 'tertiary': '#000000'},
                'abbreviation': 'PHX'
            },
            'POR': {
                'name': 'Portland Trail Blazers',
                'colors': {'primary': '#E03A3E', 'secondary': '#000000', 'tertiary': '#FFFFFF'},
                'abbreviation': 'POR'
            },
            'SAC': {
                'name': 'Sacramento Kings',
                'colors': {'primary': '#5A2D81', 'secondary': '#63727A', 'tertiary': '#000000'},
                'abbreviation': 'SAC'
            },
            'SAS': {
                'name': 'San Antonio Spurs',
                'colors': {'primary': '#C4CED4', 'secondary': '#000000', 'tertiary': '#FFFFFF'},
                'abbreviation': 'SAS'
            },
            'TOR': {
                'name': 'Toronto Raptors',
                'colors': {'primary': '#CE1141', 'secondary': '#000000', 'tertiary': '#A1A1A4'},
                'abbreviation': 'TOR'
            },
            'UTA': {
                'name': 'Utah Jazz',
                'colors': {'primary': '#002B5C', 'secondary': '#F9A01B', 'tertiary': '#00471B'},
                'abbreviation': 'UTA'
            },
            'WAS': {
                'name': 'Washington Wizards',
                'colors': {'primary': '#002B5C', 'secondary': '#E31837', 'tertiary': '#C4CED4'},
                'abbreviation': 'WAS'
            }
        }
    
    def get_logo_urls(self) -> Dict[str, Dict[str, str]]:
        """
        Get logo URLs from various CDN sources
        These are publicly available CDN URLs that work reliably
        """
        logo_sources = {}
        
        for team_abbr in self.teams.keys():
            logo_sources[team_abbr] = {
                # ESPN CDN - Most reliable, good quality
                'espn': f'https://a.espncdn.com/i/teamlogos/nba/500/{team_abbr.lower()}.png',
                
                # Alternative: NBA.com CDN (might need team ID mapping)
                # 'nba': f'https://cdn.nba.com/logos/nba/{team_id}/global/L/logo.svg',
                
                # SportsLogos.net CDN (good quality PNGs)
                'sportslogos': f'https://content.sportslogos.net/logos/6/basketball/nba/{team_abbr.lower()}_logo.png'
            }
        
        return logo_sources
    
    def download_team_logos(self, source='espn'):
        """
        Download all team logos from specified source
        
        Args:
            source: 'espn' or 'sportslogos'
        """
        logo_urls = self.get_logo_urls()
        
        for team_abbr, sources in logo_urls.items():
            if source in sources:
                url = sources[source]
                output_path = self.assets_dir / f'{team_abbr}.png'
                
                if output_path.exists():
                    print(f"✓ {team_abbr} logo already exists")
                    continue
                
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        with open(output_path, 'wb') as f:
                            f.write(response.content)
                        print(f"✓ Downloaded {team_abbr} logo")
                    else:
                        print(f"✗ Failed to download {team_abbr} logo: {response.status_code}")
                except Exception as e:
                    print(f"✗ Error downloading {team_abbr} logo: {e}")
    
    def generate_svg_placeholder(self, team_abbr: str, size: int = 100):
        """
        Generate SVG placeholder logo if download fails
        """
        team = self.teams.get(team_abbr, {})
        colors = team.get('colors', {})
        primary = colors.get('primary', '#000000')
        secondary = colors.get('secondary', '#FFFFFF')
        
        svg = f'''<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">
            <rect width="{size}" height="{size}" fill="{primary}"/>
            <text x="50%" y="50%" text-anchor="middle" dy=".3em" 
                  fill="{secondary}" font-family="Arial, sans-serif" 
                  font-size="{size//3}" font-weight="bold">
                {team_abbr}
            </text>
        </svg>'''
        
        output_path = self.assets_dir / f'{team_abbr}_placeholder.svg'
        with open(output_path, 'w') as f:
            f.write(svg)
        
        return output_path
    
    def get_team_colors(self, team_abbr: str) -> Dict[str, str]:
        """Get team colors for styling"""
        return self.teams.get(team_abbr, {}).get('colors', {})
    
    def save_team_config(self):
        """Save team configuration to JSON for easy access"""
        config_path = self.assets_dir / 'team_config.json'
        with open(config_path, 'w') as f:
            json.dump(self.teams, f, indent=2)
        print(f"✓ Team configuration saved to {config_path}")
    
    def get_logo_path(self, team_abbr: str) -> Path:
        """Get path to team logo, create placeholder if needed"""
        logo_path = self.assets_dir / f'{team_abbr}.png'
        
        if not logo_path.exists():
            # Try to download
            logo_urls = self.get_logo_urls()
            if team_abbr in logo_urls:
                url = logo_urls[team_abbr]['espn']
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        with open(logo_path, 'wb') as f:
                            f.write(response.content)
                except:
                    # Create placeholder if download fails
                    return self.generate_svg_placeholder(team_abbr)
        
        return logo_path

# Usage script
if __name__ == "__main__":
    manager = TeamAssetsManager()
    
    print("NBA Team Assets Manager")
    print("-" * 40)
    
    # Download all logos
    print("\nDownloading team logos from ESPN CDN...")
    manager.download_team_logos(source='espn')
    
    # Save configuration
    print("\nSaving team configuration...")
    manager.save_team_config()
    
    print("\n✅ Complete! Logos saved to: assets/teams/")
    print("\nTeam colors and configuration saved to: assets/teams/team_config.json")