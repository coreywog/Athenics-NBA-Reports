#!/usr/bin/env python3
"""
Matchup Report Generator
Creates HTML reports from collected matchup data
"""

import json
from pathlib import Path
from datetime import datetime
from jinja2 import Template

class MatchupReportGenerator:
    """Generate HTML matchup reports"""
    
    def __init__(self):
        self.output_dir = Path('output/html')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Team colors for styling
        self.team_colors = {
            'MIL': {'primary': '#00471B', 'secondary': '#EEE1C6'},
            'PHI': {'primary': '#006BB6', 'secondary': '#ED174C'},
            'BOS': {'primary': '#007A33', 'secondary': '#BA9653'},
            'BRO': {'primary': '#000000', 'secondary': '#FFFFFF'},
            'NYK': {'primary': '#006BB6', 'secondary': '#F58426'},
            'TOR': {'primary': '#CE1141', 'secondary': '#000000'},
            'CHI': {'primary': '#CE1141', 'secondary': '#000000'},
            'CLE': {'primary': '#860038', 'secondary': '#041E42'},
            'DET': {'primary': '#C8102E', 'secondary': '#1D42BA'},
            'IND': {'primary': '#002D62', 'secondary': '#FDBB30'},
            'ATL': {'primary': '#E03A3E', 'secondary': '#C1D32F'},
            'CHA': {'primary': '#1D1160', 'secondary': '#00788C'},
            'MIA': {'primary': '#98002E', 'secondary': '#F9A01B'},
            'ORL': {'primary': '#0077C0', 'secondary': '#C4CED4'},
            'WAS': {'primary': '#002B5C', 'secondary': '#E31837'},
            # Add more teams as needed
        }
    
    def generate_report(self, data: dict, output_filename: str = None):
        """Generate HTML report from matchup data"""
        
        # Fix logo paths to be relative from output/html/ directory
        data['away_team']['logo_path'] = f"../../assets/teams/{data['away_team']['abbreviation']}.png"
        data['home_team']['logo_path'] = f"../../assets/teams/{data['home_team']['abbreviation']}.png"
        
        # Create HTML template
        template = Template(self.get_template())
        
        # Add team colors to data
        away_abbr = data['away_team']['abbreviation']
        home_abbr = data['home_team']['abbreviation']
        data['away_team']['colors'] = self.team_colors.get(away_abbr, {'primary': '#333', 'secondary': '#666'})
        data['home_team']['colors'] = self.team_colors.get(home_abbr, {'primary': '#333', 'secondary': '#666'})
        
        # Render HTML
        html_content = template.render(data=data)
        
        # Save to file
        if not output_filename:
            output_filename = f"{away_abbr}_at_{home_abbr}_{datetime.now().strftime('%Y%m%d')}.html"
        
        output_path = self.output_dir / output_filename
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        print(f"Report generated: {output_path}")
        return output_path
    
    def get_template(self):
        """Return the HTML template"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ data.away_team.abbreviation }} @ {{ data.home_team.abbreviation }} - Matchup Report</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #1a1a1a;
            color: #fff;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Header Section */
        .header {
            background: #2a2a2a;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
        }
        
        .game-info {
            text-align: center;
            margin-bottom: 25px;
            font-size: 14px;
            color: #999;
        }
        
        .game-info span {
            margin: 0 15px;
        }
        
        .teams-container {
            display: flex;
            justify-content: space-between;
            align-items: stretch;
            gap: 30px;
        }
        
        .team-wrapper {
            flex: 1;
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .team-wrapper.away {
            flex-direction: row;
        }
        
        .team-wrapper.home {
            flex-direction: row-reverse;
        }
        
        .team-info-side {
            text-align: left;
        }
        
        .team-wrapper.home .team-info-side {
            text-align: right;
        }
        
        .team-name {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .team-location {
            font-size: 14px;
            color: #999;
            margin-bottom: 5px;
        }
        
        .team-conference {
            font-size: 12px;
            color: #777;
        }
        
        .team-logo-section {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .team-logo {
            width: 120px;
            height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .team-logo img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }
        
        .records-below-logo {
            margin-top: 15px;
            text-align: center;
            font-size: 13px;
        }
        
        .record-item {
            padding: 3px 0;
        }
        
        .record-label {
            color: #999;
            font-size: 11px;
            text-transform: uppercase;
        }
        
        .record-value {
            font-weight: bold;
            font-size: 14px;
        }
        
        .other-records {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #444;
            font-size: 12px;
            color: #888;
        }
        
        .vs-section {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-width: 150px;
        }
        
        .vs-text {
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .h2h-record {
            font-size: 18px;
            font-weight: bold;
            color: #fff;
        }
        
        /* Rankings Section */
        .section {
            background: #2a2a2a;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #444;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Placeholder styling */
        .placeholder {
            text-align: center;
            padding: 40px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Game Header Section -->
        <div class="header">
            <div class="game-info">
                <span>{{ data.game_info.city_state }}</span>
                <span>{{ data.game_info.date }}</span>
                <span>{{ data.game_info.time }}</span>
                <span>{{ data.game_info.stadium }}</span>
            </div>
            
            <div class="teams-container">
                <!-- Away Team -->
                <div class="team-wrapper away">
                    <div class="team-info-side">
                        <div class="team-name" style="color: {{ data.away_team.colors.primary }}">
                            {{ data.away_team.name }}
                        </div>
                        <div class="team-location">{{ data.away_team.city_state }}</div>
                        <div class="team-conference">
                            {{ data.away_team.conference }} Conference • {{ data.away_team.division }} Division
                        </div>
                    </div>
                    
                    <div class="team-logo-section">
                        <div class="team-logo">
                            <img src="{{ data.away_team.logo_path }}" alt="{{ data.away_team.abbreviation }}" 
                                 onerror="this.style.display='none'; this.parentElement.innerHTML='<div style=&quot;font-size:48px;font-weight:bold;color:{{ data.away_team.colors.primary }}&quot;>{{ data.away_team.abbreviation }}</div>';">
                        </div>
                        <div class="records-below-logo">
                            <div class="record-item">
                                <div class="record-label">Overall</div>
                                <div class="record-value">{{ data.away_team.records.overall }}</div>
                            </div>
                            <div class="record-item">
                                <div class="record-label">Conference</div>
                                <div class="record-value">{{ data.away_team.records.conference }}</div>
                            </div>
                            <div class="record-item">
                                <div class="record-label">Division</div>
                                <div class="record-value">{{ data.away_team.records.division }}</div>
                            </div>
                            {% if data.away_team.records.inter_conf %}
                            <div class="other-records">
                                <div class="record-label">vs West</div>
                                <div>{{ data.away_team.records.inter_conf }}</div>
                            </div>
                            {% endif %}
                        </div>
                    </div>
                </div>
                
                <!-- VS Section -->
                <div class="vs-section">
                    <div class="vs-text">Season H2H</div>
                    <div class="h2h-record">{{ data.h2h_season_record }}</div>
                </div>
                
                <!-- Home Team -->
                <div class="team-wrapper home">
                    <div class="team-info-side">
                        <div class="team-name" style="color: {{ data.home_team.colors.primary }}">
                            {{ data.home_team.name }}
                        </div>
                        <div class="team-location">{{ data.home_team.city_state }}</div>
                        <div class="team-conference">
                            {{ data.home_team.conference }} Conference • {{ data.home_team.division }} Division
                        </div>
                    </div>
                    
                    <div class="team-logo-section">
                        <div class="team-logo">
                            <img src="{{ data.home_team.logo_path }}" alt="{{ data.home_team.abbreviation }}"
                                 onerror="this.style.display='none'; this.parentElement.innerHTML='<div style=&quot;font-size:48px;font-weight:bold;color:{{ data.home_team.colors.primary }}&quot;>{{ data.home_team.abbreviation }}</div>';">
                        </div>
                        <div class="records-below-logo">
                            <div class="record-item">
                                <div class="record-label">Overall</div>
                                <div class="record-value">{{ data.home_team.records.overall }}</div>
                            </div>
                            <div class="record-item">
                                <div class="record-label">Conference</div>
                                <div class="record-value">{{ data.home_team.records.conference }}</div>
                            </div>
                            <div class="record-item">
                                <div class="record-label">Division</div>
                                <div class="record-value">{{ data.home_team.records.division }}</div>
                            </div>
                            {% if data.home_team.records.inter_conf %}
                            <div class="other-records">
                                <div class="record-label">vs West</div>
                                <div>{{ data.home_team.records.inter_conf }}</div>
                            </div>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Placeholder for Rankings Section -->
        <div class="section">
            <div class="section-title">Teams Current Rankings</div>
            <div class="placeholder">
                Rankings data will be displayed here<br>
                (To be implemented with next collector)
            </div>
        </div>
        
        <!-- Placeholder for Team Stats Section -->
        <div class="section">
            <div class="section-title">Team Stats</div>
            <div class="placeholder">
                Team statistics comparison will be displayed here<br>
                (To be implemented with stats collector)
            </div>
        </div>
        
        <!-- Placeholder for H2H Stats Section -->
        <div class="section">
            <div class="section-title">H2H Stats</div>
            <div class="placeholder">
                Head-to-head statistics will be displayed here<br>
                (Last Season vs Current Season comparison)
            </div>
        </div>
    </div>
</body>
</html>
        '''

# Test the generator
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Add project root to Python path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    from src.data.collectors.game_header import GameHeaderCollector
    
    # Collect data
    collector = GameHeaderCollector()
    data = collector.collect('MIL', 'PHI', '20250119')
    
    # Generate report
    generator = MatchupReportGenerator()
    report_path = generator.generate_report(data)
    
    print(f"\n✅ Report generated successfully!")
    print(f"Open in browser: file://{report_path.absolute()}")