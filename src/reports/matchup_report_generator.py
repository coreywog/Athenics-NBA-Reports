#!/usr/bin/env python3
"""
Enhanced Matchup Report Generator
Creates HTML reports with comprehensive home/away statistics and team stats
"""

import json
from pathlib import Path
from datetime import datetime
from jinja2 import Template

class MatchupReportGenerator:
    """Generate enhanced HTML matchup reports with home/away stats"""
    
    def __init__(self):
        self.output_dir = Path('output/html')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Team colors for styling
        self.team_colors = {
            'MIL': {'primary': '#00471B', 'secondary': '#EEE1C6'},
            'PHI': {'primary': '#006BB6', 'secondary': '#ED174C'},
            'BOS': {'primary': '#007A33', 'secondary': '#BA9653'},
            'BKN': {'primary': '#000000', 'secondary': '#FFFFFF'},
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
            'DEN': {'primary': '#0E2240', 'secondary': '#FEC524'},
            'MIN': {'primary': '#0C2340', 'secondary': '#236192'},
            'OKL': {'primary': '#007AC1', 'secondary': '#EF3B24'},
            'OKC': {'primary': '#007AC1', 'secondary': '#EF3B24'},
            'POR': {'primary': '#E03A3E', 'secondary': '#000000'},
            'UTA': {'primary': '#002B5C', 'secondary': '#00471B'},
            'GSW': {'primary': '#006BB6', 'secondary': '#FDB927'},
            'LAC': {'primary': '#C8102E', 'secondary': '#1D428A'},
            'LAL': {'primary': '#552583', 'secondary': '#FDB927'},
            'PHX': {'primary': '#1D1160', 'secondary': '#E56020'},
            'SAC': {'primary': '#5A2D81', 'secondary': '#63727A'},
            'DAL': {'primary': '#00538C', 'secondary': '#002B5E'},
            'HOU': {'primary': '#CE1141', 'secondary': '#000000'},
            'MEM': {'primary': '#5D76A9', 'secondary': '#12173F'},
            'NOP': {'primary': '#0C2340', 'secondary': '#C8102E'},
            'SAS': {'primary': '#C4CED4', 'secondary': '#000000'}
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
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Report generated: {output_path}")
        return output_path
    
    def get_template(self):
        """Return the enhanced HTML template with home/away statistics"""
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
            max-width: 1400px;
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
            align-items: flex-start;
            gap: 20px;
        }
        
        .team-wrapper {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        .team-top-section {
            display: flex;
            align-items: flex-start;
            gap: 15px;
        }
        
        .team-wrapper.away .team-top-section {
            flex-direction: row;
        }
        
        .team-wrapper.home .team-top-section {
            flex-direction: row-reverse;
        }
        
        .team-info-side {
            flex: 1;
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
            width: 120px;
            height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        
        .team-logo {
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .team-logo img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }
        
        .team-extra-records {
            display: flex;
            gap: 12px;
            margin-top: 10px;
            font-size: 11px;
            flex-wrap: wrap;
        }
        
        .team-wrapper.away .team-extra-records {
            justify-content: flex-start;
            padding-left: 10px;
        }
        
        .team-wrapper.home .team-extra-records {
            justify-content: flex-end;
            padding-right: 10px;
        }
        
        .extra-record {
            display: flex;
            gap: 4px;
            padding: 3px 6px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
        }
        
        .extra-label {
            color: #888;
            font-size: 10px;
        }
        
        .extra-value {
            font-weight: bold;
            color: #fff;
        }
        
        .center-section {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 0 20px;
        }
        
        .h2h-section {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .vs-text {
            font-size: 11px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 3px;
        }
        
        .h2h-label {
            font-size: 10px;
            color: #999;
            text-transform: uppercase;
            margin-bottom: 5px;
        }
        
        .h2h-record {
            font-size: 16px;
            font-weight: bold;
            color: #fff;
        }
        
        .records-comparison {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        
        .away-records, .home-records {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .away-records {
            text-align: right;
        }
        
        .home-records {
            text-align: left;
        }
        
        .record-labels {
            display: flex;
            flex-direction: column;
            gap: 8px;
            text-align: center;
        }
        
        .record-label {
            color: #999;
            font-size: 11px;
            text-transform: uppercase;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .record-value {
            font-weight: bold;
            font-size: 14px;
            padding: 5px 10px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
            min-width: 60px;
            text-align: center;
        }
        
        /* Streak styling */
        .extra-record .extra-value.streak-win {
            color: #4CAF50;
        }
        
        .extra-record .extra-value.streak-loss {
            color: #f44336;
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
        
        /* Team Stats Section Styles */
        .stats-table-container {
            background: #1a1a1a;
            border-radius: 8px;
            padding: 15px;
            overflow-x: auto;
            margin-bottom: 20px;
        }
        
        .team-stats-header {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #333;
        }
        
        .stats-team-logo {
            width: 40px;
            height: 40px;
            object-fit: contain;
        }
        
        .stats-team-name {
            font-size: 16px;
            font-weight: bold;
            color: #fff;
        }
        
        .stats-table-wrapper {
            overflow-x: auto;
        }
        
        .detailed-stats-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
        }
        
        .detailed-stats-table thead {
            background: #333;
        }
        
        .detailed-stats-table th {
            padding: 8px 6px;
            text-align: center;
            font-weight: 600;
            color: #ccc;
            border: 1px solid #444;
            white-space: nowrap;
        }
        
        .detailed-stats-table tbody tr {
            border-bottom: 1px solid #333;
        }
        
        .detailed-stats-table td {
            padding: 6px 4px;
            text-align: center;
            color: #fff;
            border: 1px solid #444;
        }
        
        .row-label {
            font-weight: 600;
            text-align: left !important;
            padding-left: 10px !important;
            background: #2a2a2a;
            color: #ccc;
            white-space: nowrap;
        }
        
        /* Different row colors based on time period */
        .stat-row-3game {
            background: rgba(255, 87, 87, 0.1);
        }
        
        .stat-row-7game {
            background: rgba(255, 171, 64, 0.1);
        }
        
        .stat-row-12game {
            background: rgba(64, 169, 255, 0.1);
        }
        
        .stat-row-season {
            background: rgba(76, 175, 80, 0.1);
            font-weight: 600;
        }
        
        /* Hover effects */
        .detailed-stats-table tbody tr:hover {
            background: rgba(255, 255, 255, 0.05);
        }
        
        /* Placeholder styling */
        .placeholder {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        /* Additional standings that will be added */
        .extended-records {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #333;
            font-size: 11px;
            color: #888;
        }
        
        .extended-record-item {
            padding: 3px 0;
        }
        
        /* Updated Rankings Section Styles */
        .rankings-container {
            display: flex;
            justify-content: center;
            padding-bottom: 10px;
            overflow-x: auto;
        }
        .rankings-container::-webkit-scrollbar {
            height: 8px;
        }

        .rankings-container::-webkit-scrollbar-track {
            background: #1a1a1a;
            border-radius: 4px;
        }

        .rankings-container::-webkit-scrollbar-thumb {
            background: #444;
            border-radius: 4px;
        }

        .rankings-container::-webkit-scrollbar-thumb:hover {
            background: #555;
        }

        /* Main layout with graphs on sides */
        .rankings-layout {
            display: flex;
            gap: 20px;
            align-items: stretch;
            width: fit-content;
            margin: 0 auto;
            justify-content: center;
        }

        .graph-container-left {
            flex: 0 0 450px;
            width: 470px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            padding: 12px;
            border: 1px solid #3a3a3a;
            display: flex;
            flex-direction: column;
        }

        .rankings-table-center {
            flex: 0 0 auto;
            display: flex;
            align-items: stretch;
        }

        .graph-container-right {
            flex: 0 0 450px;
            width: 470px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            padding: 12px;
            border: 1px solid #3a3a3a;
            display: flex;
            flex-direction: column;
        }

        /* Rankings Table Wrapper - matching stats table style */
        .rankings-table-wrapper {
            background: rgba(255, 255, 255, 0.02);
            border-radius: 8px;
            padding: 15px;
            overflow-x: auto;
            border: 1px solid #3a3a3a;
        }

        .rankings-comparison-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        .rankings-comparison-table thead {
            background: #333;
        }

        .rankings-comparison-table thead th {
            padding: 10px 8px;
            text-align: center;
            font-weight: 600;
            color: #ccc;
            border: 1px solid #444;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
        }

        .rankings-comparison-table thead th.team-column {
            width: 30%;
            background: rgba(255, 255, 255, 0.05);
            color: #fff;
            font-size: 13px;
        }

        .rankings-comparison-table thead th.stat-name-column {
            width: 40%;
            background: #2a2a2a;
            color: #999;
        }

        .rankings-comparison-table tbody tr {
            border-bottom: 1px solid #333;
        }

        .rankings-comparison-table tbody tr:hover {
            background: rgba(255, 255, 255, 0.03);
        }

        .rankings-comparison-table tbody td {
            padding: 8px;
            text-align: center;
            border: 1px solid #444;
        }

        .rank-value {
            font-size: 16px;
            font-weight: bold;
            color: #fff;
            background: rgba(255, 255, 255, 0.02);
        }

        .rank-label {
            font-size: 11px;
            font-weight: 600;
            color: #999;
            background: #2a2a2a;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Color coding for top rankings */
        .rank-top5 {
            color: #4CAF50 !important;
        }

        .rank-top10 {
            color: #8BC34A !important;
        }

        .rank-top15 {
            color: #FFC107 !important;
        }

        /* Graph styling updates */
        .graph-header {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #3a3a3a;
        }

        .graph-team-logo {
            width: 25px;
            height: 25px;
            object-fit: contain;
        }

        .graph-title {
            font-size: 12px;
            font-weight: 600;
            color: #ccc;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        #awayRankingsChart,
        #homeRankingsChart {
            display: block;
            margin: 0 auto;
            border-radius: 4px;
        }

        @media (max-width: 768px) {
            .rankings-graphs-bottom {
                flex-direction: column;
            }
            
            .rank-value {
                font-size: 14px;
            }
            
            .rank-label {
                font-size: 10px;
            }
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
                    <div class="team-top-section">
                        <div class="team-info-side">
                            <div class="team-name" style="color: {{ data.away_team.colors.primary }}">
                                {{ data.away_team.name }}
                            </div>
                            <div class="team-location">
                                {{ data.away_team.city_state }} - {{ data.away_team.abbreviation }}
                            </div>
                            <div class="team-conference">
                                {{ data.away_team.conference }} Conference | {{ data.away_team.division }} Division
                            </div>
                        </div>
                        
                        <div class="team-logo-section">
                            <div class="team-logo">
                                <img src="{{ data.away_team.logo_path }}" alt="{{ data.away_team.abbreviation }}">
                            </div>
                        </div>
                    </div>
                    
                    <div class="team-extra-records">
                        <div class="extra-record">
                            <span class="extra-label">Division:</span>
                            <span class="extra-value">{{ data.away_team.records.division }}</span>
                        </div>
                        <div class="extra-record">
                            <span class="extra-label">Home:</span>
                            <span class="extra-value">{{ data.away_team.records.home }}</span>
                        </div>
                        <div class="extra-record">
                            <span class="extra-label">Away:</span>
                            <span class="extra-value">{{ data.away_team.records.away }}</span>
                        </div>
                        <div class="extra-record">
                            <span class="extra-label">Streak:</span>
                            <span class="extra-value {% if 'W' in data.away_team.records.streak %}class="streak-win"{% elif 'L' in data.away_team.records.streak %}class="streak-loss"{% endif %}">
                                {{ data.away_team.records.streak }}
                            </span>
                        </div>
                    </div>
                    
                    <div class="team-extra-records">
                        <div class="extra-record">
                            <span class="extra-label">Last 12:</span>
                            <span class="extra-value">{{ data.away_team.records.last_12 }}</span>
                        </div>
                        <div class="extra-record">
                            <span class="extra-label">Last 7:</span>
                            <span class="extra-value">{{ data.away_team.records.last_7 }}</span>
                        </div>
                        <div class="extra-record">
                            <span class="extra-label">Last 3:</span>
                            <span class="extra-value">{{ data.away_team.records.last_3 }}</span>
                        </div>
                    </div>
                </div>
                
                <!-- Center Section with H2H and Records -->
                <div class="center-section">
                    <div class="h2h-section">
                        <div class="vs-text">vs</div>
                        <div class="h2h-label">Season H2H</div>
                        <div class="h2h-record">{{ data.h2h_season_record }}</div>
                    </div>
                    
                    <div class="records-comparison">
                        <div class="away-records">
                            <div class="record-value">{{ data.away_team.records.overall }}</div>
                            <div class="record-value">{{ data.away_team.records.vs_eastern }}</div>
                            <div class="record-value">{{ data.away_team.records.vs_western }}</div>
                        </div>
                        
                        <div class="record-labels">
                            <div class="record-label">Overall</div>
                            <div class="record-label">vs Eastern</div>
                            <div class="record-label">vs Western</div>
                        </div>
                        
                        <div class="home-records">
                            <div class="record-value">{{ data.home_team.records.overall }}</div>
                            <div class="record-value">{{ data.home_team.records.vs_eastern }}</div>
                            <div class="record-value">{{ data.home_team.records.vs_western }}</div>
                        </div>
                    </div>
                </div>
                
                <!-- Home Team -->
                <div class="team-wrapper home">
                    <div class="team-top-section">
                        <div class="team-info-side">
                            <div class="team-name" style="color: {{ data.home_team.colors.primary }}">
                                {{ data.home_team.name }}
                            </div>
                            <div class="team-location">
                                {{ data.home_team.city_state }} - {{ data.home_team.abbreviation }}
                            </div>
                            <div class="team-conference">
                                {{ data.home_team.conference }} Conference | {{ data.home_team.division }} Division
                            </div>
                        </div>
                        
                        <div class="team-logo-section">
                            <div class="team-logo">
                                <img src="{{ data.home_team.logo_path }}" alt="{{ data.home_team.abbreviation }}">
                            </div>
                        </div>
                    </div>
                    
                    <div class="team-extra-records">
                        <div class="extra-record reversed">
                            <span class="extra-value {% if 'W' in data.home_team.records.streak %}class="streak-win"{% elif 'L' in data.home_team.records.streak %}class="streak-loss"{% endif %}">
                                {{ data.home_team.records.streak }}
                            </span>
                            <span class="extra-label">:Streak</span>
                        </div>
                        <div class="extra-record reversed">
                            <span class="extra-value">{{ data.home_team.records.away }}</span>
                            <span class="extra-label">:Away</span>
                        </div>
                        <div class="extra-record reversed">
                            <span class="extra-value">{{ data.home_team.records.home }}</span>
                            <span class="extra-label">:Home</span>
                        </div>
                        <div class="extra-record reversed">
                            <span class="extra-value">{{ data.home_team.records.division }}</span>
                            <span class="extra-label">:Division</span>
                        </div>
                    </div>
                    
                    <div class="team-extra-records">
                        <div class="extra-record reversed">
                            <span class="extra-value">{{ data.home_team.records.last_3 }}</span>
                            <span class="extra-label">:Last 3</span>
                        </div>
                        <div class="extra-record reversed">
                            <span class="extra-value">{{ data.home_team.records.last_7 }}</span>
                            <span class="extra-label">:Last 7</span>
                        </div>
                        <div class="extra-record reversed">
                            <span class="extra-value">{{ data.home_team.records.last_12 }}</span>
                            <span class="extra-label">:Last 12</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Teams Current Statistics Section -->
        <div class="section">
            <div class="section-title">Teams Current Statistics</div>
            
            <!-- Away Team Stats Table -->
            <div class="stats-table-container">
                <div class="team-stats-header">
                    <img src="{{ data.away_team.logo_path }}" alt="{{ data.away_team.abbreviation }}" class="stats-team-logo">
                    <span class="stats-team-name">{{ data.away_team.name }}</span>
                </div>
                <div class="stats-table-wrapper">
                    <table class="detailed-stats-table">
                        <thead>
                            <tr>
                                <th></th>
                                <th>PS</th>
                                <th>PA</th>
                                <th>FG</th>
                                <th>FGA</th>
                                <th>FG%</th>
                                <th>3P</th>
                                <th>3PA</th>
                                <th>3P%</th>
                                <th>2P</th>
                                <th>2PA</th>
                                <th>2P%</th>
                                <th>FT</th>
                                <th>FTA</th>
                                <th>FT%</th>
                                <th>ORB</th>
                                <th>DRB</th>
                                <th>TRB</th>
                                <th>AST</th>
                                <th>STL</th>
                                <th>BLK</th>
                                <th>TOV</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% if 'away_rolling_stats' in data %}
                            <tr class="stat-row-3game">
                                <td class="row-label">Last 3</td>
                                <td>{{ data.away_rolling_stats.last_3.ps }}</td>
                                <td>{{ data.away_rolling_stats.last_3.pa }}</td>
                                <td>{{ data.away_rolling_stats.last_3.fg }}</td>
                                <td>{{ data.away_rolling_stats.last_3.fga }}</td>
                                <td>{{ data.away_rolling_stats.last_3.fg_pct }}</td>
                                <td>{{ data.away_rolling_stats.last_3.three_p }}</td>
                                <td>{{ data.away_rolling_stats.last_3.three_pa }}</td>
                                <td>{{ data.away_rolling_stats.last_3.three_pct }}</td>
                                <td>{{ data.away_rolling_stats.last_3.two_p }}</td>
                                <td>{{ data.away_rolling_stats.last_3.two_pa }}</td>
                                <td>{{ data.away_rolling_stats.last_3.two_pct }}</td>
                                <td>{{ data.away_rolling_stats.last_3.ft }}</td>
                                <td>{{ data.away_rolling_stats.last_3.fta }}</td>
                                <td>{{ data.away_rolling_stats.last_3.ft_pct }}</td>
                                <td>{{ data.away_rolling_stats.last_3.orb }}</td>
                                <td>{{ data.away_rolling_stats.last_3.drb }}</td>
                                <td>{{ data.away_rolling_stats.last_3.trb }}</td>
                                <td>{{ data.away_rolling_stats.last_3.ast }}</td>
                                <td>{{ data.away_rolling_stats.last_3.stl }}</td>
                                <td>{{ data.away_rolling_stats.last_3.blk }}</td>
                                <td>{{ data.away_rolling_stats.last_3.tov }}</td>
                            </tr>
                            <tr class="stat-row-7game">
                                <td class="row-label">Last 7</td>
                                <td>{{ data.away_rolling_stats.last_7.ps }}</td>
                                <td>{{ data.away_rolling_stats.last_7.pa }}</td>
                                <td>{{ data.away_rolling_stats.last_7.fg }}</td>
                                <td>{{ data.away_rolling_stats.last_7.fga }}</td>
                                <td>{{ data.away_rolling_stats.last_7.fg_pct }}</td>
                                <td>{{ data.away_rolling_stats.last_7.three_p }}</td>
                                <td>{{ data.away_rolling_stats.last_7.three_pa }}</td>
                                <td>{{ data.away_rolling_stats.last_7.three_pct }}</td>
                                <td>{{ data.away_rolling_stats.last_7.two_p }}</td>
                                <td>{{ data.away_rolling_stats.last_7.two_pa }}</td>
                                <td>{{ data.away_rolling_stats.last_7.two_pct }}</td>
                                <td>{{ data.away_rolling_stats.last_7.ft }}</td>
                                <td>{{ data.away_rolling_stats.last_7.fta }}</td>
                                <td>{{ data.away_rolling_stats.last_7.ft_pct }}</td>
                                <td>{{ data.away_rolling_stats.last_7.orb }}</td>
                                <td>{{ data.away_rolling_stats.last_7.drb }}</td>
                                <td>{{ data.away_rolling_stats.last_7.trb }}</td>
                                <td>{{ data.away_rolling_stats.last_7.ast }}</td>
                                <td>{{ data.away_rolling_stats.last_7.stl }}</td>
                                <td>{{ data.away_rolling_stats.last_7.blk }}</td>
                                <td>{{ data.away_rolling_stats.last_7.tov }}</td>
                            </tr>
                            <tr class="stat-row-12game">
                                <td class="row-label">Last 12</td>
                                <td>{{ data.away_rolling_stats.last_12.ps }}</td>
                                <td>{{ data.away_rolling_stats.last_12.pa }}</td>
                                <td>{{ data.away_rolling_stats.last_12.fg }}</td>
                                <td>{{ data.away_rolling_stats.last_12.fga }}</td>
                                <td>{{ data.away_rolling_stats.last_12.fg_pct }}</td>
                                <td>{{ data.away_rolling_stats.last_12.three_p }}</td>
                                <td>{{ data.away_rolling_stats.last_12.three_pa }}</td>
                                <td>{{ data.away_rolling_stats.last_12.three_pct }}</td>
                                <td>{{ data.away_rolling_stats.last_12.two_p }}</td>
                                <td>{{ data.away_rolling_stats.last_12.two_pa }}</td>
                                <td>{{ data.away_rolling_stats.last_12.two_pct }}</td>
                                <td>{{ data.away_rolling_stats.last_12.ft }}</td>
                                <td>{{ data.away_rolling_stats.last_12.fta }}</td>
                                <td>{{ data.away_rolling_stats.last_12.ft_pct }}</td>
                                <td>{{ data.away_rolling_stats.last_12.orb }}</td>
                                <td>{{ data.away_rolling_stats.last_12.drb }}</td>
                                <td>{{ data.away_rolling_stats.last_12.trb }}</td>
                                <td>{{ data.away_rolling_stats.last_12.ast }}</td>
                                <td>{{ data.away_rolling_stats.last_12.stl }}</td>
                                <td>{{ data.away_rolling_stats.last_12.blk }}</td>
                                <td>{{ data.away_rolling_stats.last_12.tov }}</td>
                            </tr>
                            {% else %}
                            <tr class="stat-row-3game">
                                <td class="row-label">Last 3</td>
                                <td colspan="21">Data not available - add RollingStatsCollector</td>
                            </tr>
                            <tr class="stat-row-7game">
                                <td class="row-label">Last 7</td>
                                <td colspan="21">Data not available - add RollingStatsCollector</td>
                            </tr>
                            <tr class="stat-row-12game">
                                <td class="row-label">Last 12</td>
                                <td colspan="21">Data not available - add RollingStatsCollector</td>
                            </tr>
                            {% endif %}
                            <tr class="stat-row-season">
                                <td class="row-label">Season</td>
                                {% if 'away_team_stats' in data and data.away_team_stats.offensive %}
                                <td>{{ data.away_team_stats.offensive.ppg }}</td>
                                <td>{{ data.away_team_stats.defensive.opp_ppg }}</td>
                                <td>{{ data.away_team_stats.offensive.fg_made }}</td>
                                <td>{{ data.away_team_stats.offensive.fg_att }}</td>
                                <td>{{ data.away_team_stats.offensive.fg_pct }}</td>
                                <td>{{ data.away_team_stats.offensive.three_made }}</td>
                                <td>{{ data.away_team_stats.offensive.three_att }}</td>
                                <td>{{ data.away_team_stats.offensive.three_pct }}</td>
                                <td>{{ (data.away_team_stats.offensive.fg_made - data.away_team_stats.offensive.three_made)|round(1) }}</td>
                                <td>{{ (data.away_team_stats.offensive.fg_att - data.away_team_stats.offensive.three_att)|round(1) }}</td>
                                <td>{{ (((data.away_team_stats.offensive.fg_made - data.away_team_stats.offensive.three_made) / (data.away_team_stats.offensive.fg_att - data.away_team_stats.offensive.three_att) * 100) if (data.away_team_stats.offensive.fg_att - data.away_team_stats.offensive.three_att) > 0 else 0)|round(1) }}</td>
                                <td>{{ data.away_team_stats.offensive.ft_made }}</td>
                                <td>{{ data.away_team_stats.offensive.ft_att }}</td>
                                <td>{{ data.away_team_stats.offensive.ft_pct }}</td>
                                <td>{{ data.away_team_stats.defensive.off_reb }}</td>
                                <td>{{ data.away_team_stats.defensive.def_reb }}</td>
                                <td>{{ data.away_team_stats.defensive.reb }}</td>
                                <td>{{ data.away_team_stats.offensive.ast }}</td>
                                <td>{{ data.away_team_stats.defensive.stl }}</td>
                                <td>{{ data.away_team_stats.defensive.blk }}</td>
                                <td>{{ data.away_team_stats.offensive.turnovers }}</td>
                                {% else %}
                                <td colspan="21">Data not available</td>
                                {% endif %}
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Home Team Stats Table -->
            <div class="stats-table-container">
                <div class="team-stats-header">
                    <img src="{{ data.home_team.logo_path }}" alt="{{ data.home_team.abbreviation }}" class="stats-team-logo">
                    <span class="stats-team-name">{{ data.home_team.name }}</span>
                </div>
                <div class="stats-table-wrapper">
                    <table class="detailed-stats-table">
                        <thead>
                            <tr>
                                <th></th>
                                <th>PS</th>
                                <th>PA</th>
                                <th>FG</th>
                                <th>FGA</th>
                                <th>FG%</th>
                                <th>3P</th>
                                <th>3PA</th>
                                <th>3P%</th>
                                <th>2P</th>
                                <th>2PA</th>
                                <th>2P%</th>
                                <th>FT</th>
                                <th>FTA</th>
                                <th>FT%</th>
                                <th>ORB</th>
                                <th>DRB</th>
                                <th>TRB</th>
                                <th>AST</th>
                                <th>STL</th>
                                <th>BLK</th>
                                <th>TOV</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% if data.home_rolling_stats %}
                            <tr class="stat-row-3game">
                                <td class="row-label">Last 3</td>
                                <td>{{ data.home_rolling_stats.last_3.ps }}</td>
                                <td>{{ data.home_rolling_stats.last_3.pa }}</td>
                                <td>{{ data.home_rolling_stats.last_3.fg }}</td>
                                <td>{{ data.home_rolling_stats.last_3.fga }}</td>
                                <td>{{ data.home_rolling_stats.last_3.fg_pct }}</td>
                                <td>{{ data.home_rolling_stats.last_3.three_p }}</td>
                                <td>{{ data.home_rolling_stats.last_3.three_pa }}</td>
                                <td>{{ data.home_rolling_stats.last_3.three_pct }}</td>
                                <td>{{ data.home_rolling_stats.last_3.two_p }}</td>
                                <td>{{ data.home_rolling_stats.last_3.two_pa }}</td>
                                <td>{{ data.home_rolling_stats.last_3.two_pct }}</td>
                                <td>{{ data.home_rolling_stats.last_3.ft }}</td>
                                <td>{{ data.home_rolling_stats.last_3.fta }}</td>
                                <td>{{ data.home_rolling_stats.last_3.ft_pct }}</td>
                                <td>{{ data.home_rolling_stats.last_3.orb }}</td>
                                <td>{{ data.home_rolling_stats.last_3.drb }}</td>
                                <td>{{ data.home_rolling_stats.last_3.trb }}</td>
                                <td>{{ data.home_rolling_stats.last_3.ast }}</td>
                                <td>{{ data.home_rolling_stats.last_3.stl }}</td>
                                <td>{{ data.home_rolling_stats.last_3.blk }}</td>
                                <td>{{ data.home_rolling_stats.last_3.tov }}</td>
                            </tr>
                            <tr class="stat-row-7game">
                                <td class="row-label">Last 7</td>
                                <td>{{ data.home_rolling_stats.last_7.ps }}</td>
                                <td>{{ data.home_rolling_stats.last_7.pa }}</td>
                                <td>{{ data.home_rolling_stats.last_7.fg }}</td>
                                <td>{{ data.home_rolling_stats.last_7.fga }}</td>
                                <td>{{ data.home_rolling_stats.last_7.fg_pct }}</td>
                                <td>{{ data.home_rolling_stats.last_7.three_p }}</td>
                                <td>{{ data.home_rolling_stats.last_7.three_pa }}</td>
                                <td>{{ data.home_rolling_stats.last_7.three_pct }}</td>
                                <td>{{ data.home_rolling_stats.last_7.two_p }}</td>
                                <td>{{ data.home_rolling_stats.last_7.two_pa }}</td>
                                <td>{{ data.home_rolling_stats.last_7.two_pct }}</td>
                                <td>{{ data.home_rolling_stats.last_7.ft }}</td>
                                <td>{{ data.home_rolling_stats.last_7.fta }}</td>
                                <td>{{ data.home_rolling_stats.last_7.ft_pct }}</td>
                                <td>{{ data.home_rolling_stats.last_7.orb }}</td>
                                <td>{{ data.home_rolling_stats.last_7.drb }}</td>
                                <td>{{ data.home_rolling_stats.last_7.trb }}</td>
                                <td>{{ data.home_rolling_stats.last_7.ast }}</td>
                                <td>{{ data.home_rolling_stats.last_7.stl }}</td>
                                <td>{{ data.home_rolling_stats.last_7.blk }}</td>
                                <td>{{ data.home_rolling_stats.last_7.tov }}</td>
                            </tr>
                            <tr class="stat-row-12game">
                                <td class="row-label">Last 12</td>
                                <td>{{ data.home_rolling_stats.last_12.ps }}</td>
                                <td>{{ data.home_rolling_stats.last_12.pa }}</td>
                                <td>{{ data.home_rolling_stats.last_12.fg }}</td>
                                <td>{{ data.home_rolling_stats.last_12.fga }}</td>
                                <td>{{ data.home_rolling_stats.last_12.fg_pct }}</td>
                                <td>{{ data.home_rolling_stats.last_12.three_p }}</td>
                                <td>{{ data.home_rolling_stats.last_12.three_pa }}</td>
                                <td>{{ data.home_rolling_stats.last_12.three_pct }}</td>
                                <td>{{ data.home_rolling_stats.last_12.two_p }}</td>
                                <td>{{ data.home_rolling_stats.last_12.two_pa }}</td>
                                <td>{{ data.home_rolling_stats.last_12.two_pct }}</td>
                                <td>{{ data.home_rolling_stats.last_12.ft }}</td>
                                <td>{{ data.home_rolling_stats.last_12.fta }}</td>
                                <td>{{ data.home_rolling_stats.last_12.ft_pct }}</td>
                                <td>{{ data.home_rolling_stats.last_12.orb }}</td>
                                <td>{{ data.home_rolling_stats.last_12.drb }}</td>
                                <td>{{ data.home_rolling_stats.last_12.trb }}</td>
                                <td>{{ data.home_rolling_stats.last_12.ast }}</td>
                                <td>{{ data.home_rolling_stats.last_12.stl }}</td>
                                <td>{{ data.home_rolling_stats.last_12.blk }}</td>
                                <td>{{ data.home_rolling_stats.last_12.tov }}</td>
                            </tr>
                            {% else %}
                            <tr class="stat-row-3game">
                                <td class="row-label">Last 3</td>
                                <td colspan="21">Data not available - add RollingStatsCollector</td>
                            </tr>
                            <tr class="stat-row-7game">
                                <td class="row-label">Last 7</td>
                                <td colspan="21">Data not available - add RollingStatsCollector</td>
                            </tr>
                            <tr class="stat-row-12game">
                                <td class="row-label">Last 12</td>
                                <td colspan="21">Data not available - add RollingStatsCollector</td>
                            </tr>
                            {% endif %}
                            <tr class="stat-row-season">
                                <td class="row-label">Season</td>
                                {% if 'home_team_stats' in data and data.home_team_stats.offensive %}
                                <td>{{ data.home_team_stats.offensive.ppg }}</td>
                                <td>{{ data.home_team_stats.defensive.opp_ppg }}</td>
                                <td>{{ data.home_team_stats.offensive.fg_made }}</td>
                                <td>{{ data.home_team_stats.offensive.fg_att }}</td>
                                <td>{{ data.home_team_stats.offensive.fg_pct }}</td>
                                <td>{{ data.home_team_stats.offensive.three_made }}</td>
                                <td>{{ data.home_team_stats.offensive.three_att }}</td>
                                <td>{{ data.home_team_stats.offensive.three_pct }}</td>
                                <td>{{ (data.home_team_stats.offensive.fg_made - data.home_team_stats.offensive.three_made)|round(1) }}</td>
                                <td>{{ (data.home_team_stats.offensive.fg_att - data.home_team_stats.offensive.three_att)|round(1) }}</td>
                                <td>{{ (((data.home_team_stats.offensive.fg_made - data.home_team_stats.offensive.three_made) / (data.home_team_stats.offensive.fg_att - data.home_team_stats.offensive.three_att) * 100) if (data.home_team_stats.offensive.fg_att - data.home_team_stats.offensive.three_att) > 0 else 0)|round(1) }}</td>
                                <td>{{ data.home_team_stats.offensive.ft_made }}</td>
                                <td>{{ data.home_team_stats.offensive.ft_att }}</td>
                                <td>{{ data.home_team_stats.offensive.ft_pct }}</td>
                                <td>{{ data.home_team_stats.defensive.off_reb }}</td>
                                <td>{{ data.home_team_stats.defensive.def_reb }}</td>
                                <td>{{ data.home_team_stats.defensive.reb }}</td>
                                <td>{{ data.home_team_stats.offensive.ast }}</td>
                                <td>{{ data.home_team_stats.defensive.stl }}</td>
                                <td>{{ data.home_team_stats.defensive.blk }}</td>
                                <td>{{ data.home_team_stats.offensive.turnovers }}</td>
                                {% else %}
                                <td colspan="21">Data not available</td>
                                {% endif %}
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Teams Current Rankings Section - UPDATED -->
        <div class="section">
            <div class="section-title">Teams Current Rankings</div>
            
            <div class="rankings-container">
                <!-- Main layout with graphs on sides -->
                <div class="rankings-layout">
                    <!-- Left Graph -->
                    <div class="graph-container-left">
                        <div class="graph-header">
                            <img src="{{ data.away_team.logo_path }}" alt="{{ data.away_team.abbreviation }}" class="graph-team-logo">
                            <span class="graph-title">{{ data.away_team.abbreviation }} - Last 12 Games</span>
                        </div>
                        <canvas id="awayRankingsChart" width="440" height="470"></canvas>
                    </div>
                    
                    <!-- Center Rankings Table -->
                    <div class="rankings-table-center">
                        <div class="rankings-table-wrapper">
                            <table class="rankings-comparison-table">
                                <thead>
                                    <tr>
                                        <th class="team-column">{{ data.away_team.abbreviation }}</th>
                                        <th class="stat-name-column">Ranking Category</th>
                                        <th class="team-column">{{ data.home_team.abbreviation }}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td class="rank-value away-value" id="away-overall">{{ data.away_rankings.overall if data.away_rankings else '-' }}</td>
                                        <td class="rank-label">Overall Rank</td>
                                        <td class="rank-value home-value" id="home-overall">{{ data.home_rankings.overall if data.home_rankings else '-' }}</td>
                                    </tr>
                                    <tr>
                                        <td class="rank-value away-value" id="away-offensive">{{ data.away_rankings.offensive if data.away_rankings else '-' }}</td>
                                        <td class="rank-label">Overall Off. Rank</td>
                                        <td class="rank-value home-value" id="home-offensive">{{ data.home_rankings.offensive if data.home_rankings else '-' }}</td>
                                    </tr>
                                    <tr>
                                        <td class="rank-value away-value" id="away-defensive">{{ data.away_rankings.defensive if data.away_rankings else '-' }}</td>
                                        <td class="rank-label">Overall Def. Rank</td>
                                        <td class="rank-value home-value" id="home-defensive">{{ data.home_rankings.defensive if data.home_rankings else '-' }}</td>
                                    </tr>
                                    <tr>
                                        <td class="rank-value away-value" id="away-conference">{{ data.away_rankings.conference if data.away_rankings else '-' }}</td>
                                        <td class="rank-label">Conf. Rank</td>
                                        <td class="rank-value home-value" id="home-conference">{{ data.home_rankings.conference if data.home_rankings else '-' }}</td>
                                    </tr>
                                    <tr>
                                        <td class="rank-value away-value">{{ data.away_rankings.conference_offensive if data.away_rankings else '-' }}</td>
                                        <td class="rank-label">Conf. Off. Rank</td>
                                        <td class="rank-value home-value">{{ data.home_rankings.conference_offensive if data.home_rankings else '-' }}</td>
                                    </tr>
                                    <tr>
                                        <td class="rank-value away-value">{{ data.away_rankings.conference_defensive if data.away_rankings else '-' }}</td>
                                        <td class="rank-label">Conf. Def. Rank</td>
                                        <td class="rank-value home-value">{{ data.home_rankings.conference_defensive if data.home_rankings else '-' }}</td>
                                    </tr>
                                    <tr>
                                        <td class="rank-value away-value" id="away-division">{{ data.away_rankings.division if data.away_rankings else '-' }}</td>
                                        <td class="rank-label">Div. Rank</td>
                                        <td class="rank-value home-value" id="home-division">{{ data.home_rankings.division if data.home_rankings else '-' }}</td>
                                    </tr>
                                    <tr>
                                        <td class="rank-value away-value">{{ data.away_rankings.division_offensive if data.away_rankings else '-' }}</td>
                                        <td class="rank-label">Div. Off. Rank</td>
                                        <td class="rank-value home-value">{{ data.home_rankings.division_offensive if data.home_rankings else '-' }}</td>
                                    </tr>
                                    <tr>
                                        <td class="rank-value away-value">{{ data.away_rankings.division_defensive if data.away_rankings else '-' }}</td>
                                        <td class="rank-label">Div. Def. Rank</td>
                                        <td class="rank-value home-value">{{ data.home_rankings.division_defensive if data.home_rankings else '-' }}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <!-- Right Graph -->
                    <div class="graph-container-right">
                        <div class="graph-header">
                            <img src="{{ data.home_team.logo_path }}" alt="{{ data.home_team.abbreviation }}" class="graph-team-logo">
                            <span class="graph-title">{{ data.home_team.abbreviation }} - Last 12 Games</span>
                        </div>
                        <canvas id="homeRankingsChart" width="440" height="470"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Placeholder for H2H Stats Section -->
        <div class="section">
            <div class="section-title">H2H Historical Stats</div>
            <div class="placeholder">
                Head-to-head statistics will be displayed here<br>
                Last 5 meetings, average scores, trends<br>
                (To be implemented with H2H collector)
            </div>
        </div>
        
        <!-- Placeholder for Player Matchups Section -->
        <div class="section">
            <div class="section-title">Key Player Matchups</div>
            <div class="placeholder">
                Player vs Player statistics<br>
                Star player performances, injury report<br>
                (To be implemented with player collector)
            </div>
        </div>
    </div>

<script>
// Updated function to draw line chart with real data
function drawRankingsChart(canvasId, teamAbbr, teamColor) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Get real data from Python backend
    let historicalData;
    if (canvasId === 'awayRankingsChart') {
        historicalData = {{ data.away_rankings.historical | tojson }};
    } else {
        historicalData = {{ data.home_rankings.historical | tojson }};
    }
    
    // Extract data from historical records
    const games = historicalData.map((d, i) => `G${i + 1}`);
    const overallRanks = historicalData.map(d => d.overall_rank || 15);
    const offRanks = historicalData.map(d => d.offensive_rank || 15);
    const defRanks = historicalData.map(d => d.defensive_rank || 15);
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Set up chart dimensions
    const padding = { top: 35, right: 45, bottom: 35, left: 45 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;
    
    // Background with subtle gradient
    const bgGradient = ctx.createLinearGradient(0, 0, 0, height);
    bgGradient.addColorStop(0, '#2a2a2a');
    bgGradient.addColorStop(1, '#252525');
    ctx.fillStyle = bgGradient;
    ctx.fillRect(0, 0, width, height);
    
    // Draw grid
    ctx.strokeStyle = '#3a3a3a';
    ctx.lineWidth = 1;
    ctx.setLineDash([2, 2]);
    
    // Horizontal grid lines
    for (let i = 0; i <= 5; i++) {
        const y = padding.top + (chartHeight / 5) * i;
        ctx.beginPath();
        ctx.moveTo(padding.left, y);
        ctx.lineTo(width - padding.right, y);
        ctx.stroke();
    }
    
    // Vertical grid lines
    for (let i = 0; i < games.length; i++) {
        const x = padding.left + (chartWidth / (games.length - 1)) * i;
        ctx.beginPath();
        ctx.moveTo(x, padding.top);
        ctx.lineTo(x, height - padding.bottom);
        ctx.stroke();
    }
    
    ctx.setLineDash([]);
    
    // Draw axes
    ctx.strokeStyle = '#4a4a4a';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding.left, padding.top);
    ctx.lineTo(padding.left, height - padding.bottom);
    ctx.lineTo(width - padding.right, height - padding.bottom);
    ctx.stroke();
    
    // Function to scale values
    const scaleX = (index) => padding.left + (index * chartWidth / (games.length - 1));
    const scaleY = (rank) => padding.top + ((rank - 1) / 29) * chartHeight;
    
    // Draw lines with smooth curves
    const drawSmoothLine = (data, color, lineWidth = 2) => {
        // Add glow effect
        ctx.shadowColor = color;
        ctx.shadowBlur = 4;
        
        ctx.strokeStyle = color;
        ctx.lineWidth = lineWidth;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        
        // Draw line
        ctx.beginPath();
        for (let i = 0; i < data.length; i++) {
            const x = scaleX(i);
            const y = scaleY(data[i]);
            
            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);  // Simple straight line
            }
        }
        ctx.stroke();
        
        // Reset shadow
        ctx.shadowColor = 'transparent';
        ctx.shadowBlur = 0;
        
        // Draw points
        for (let i = 0; i < data.length; i++) {
            const x = scaleX(i);
            const y = scaleY(data[i]);
            
            // Outer circle
            ctx.fillStyle = '#2a2a2a';
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, 2 * Math.PI);
            ctx.fill();
            
            // Inner circle
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(x, y, 2.5, 0, 2 * Math.PI);
            ctx.fill();
        }
    };
    
    // Draw the three lines
    drawSmoothLine(defRanks, '#40A9FF', 2);      // Blue for defensive
    drawSmoothLine(offRanks, '#FF6B6B', 2);      // Red for offensive  
    drawSmoothLine(overallRanks, '#4CAF50', 2.5); // Green for overall (thicker)
    
    // Draw labels
    ctx.fillStyle = '#888';
    ctx.font = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
    ctx.textAlign = 'center';
    
    // X-axis labels (games) - show every other
    ctx.fillStyle = '#bbb';  // Lighter color for better visibility
    ctx.font = 'bold 11px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
    ctx.textAlign = 'center';

    for (let i = 0; i < games.length; i += 2) {
        const x = scaleX(i);
        ctx.fillText(games[i], x, height - padding.bottom + 18);
    }
    
    // Y-axis labels (rankings)
    ctx.save();
    ctx.translate(15, height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.textAlign = 'center';
    ctx.fillStyle = '#bbb';  // Lighter color
    ctx.font = 'bold 11px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
    ctx.fillText('LEAGUE RANK', 0, 0);
    ctx.restore();
    for (let i = 0; i <= 5; i++) {
        const rank = 1 + i * 6;
        const y = padding.top + (chartHeight / 5) * i;
        ctx.fillText(rank.toString(), padding.left - 8, y + 3);
    }
    
    // Y-axis title
    ctx.save();
    ctx.translate(12, height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.textAlign = 'center';
    ctx.fillStyle = '#666';
    ctx.font = '9px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
    ctx.fillText('RANK', 0, 0);
    ctx.restore();
    
    // Legend
    const legendY = 15;
    const legendItems = [
        { color: '#4CAF50', label: 'Overall' },
        { color: '#FF6B6B', label: 'Offensive' },
        { color: '#40A9FF', label: 'Defensive' }
    ];

    // Calculate total legend width
    const itemWidth = 75;
    const totalLegendWidth = legendItems.length * itemWidth;
    const legendStartX = (width - totalLegendWidth) / 2;  // Center the legend

    // Bigger, clearer legend
    ctx.font = 'bold 11px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';

    let currentX = legendStartX;
    legendItems.forEach(item => {
        // Draw thicker line
        ctx.strokeStyle = item.color;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(currentX, legendY);
        ctx.lineTo(currentX + 15, legendY);
        ctx.stroke();
        
        // Draw label with better contrast
        ctx.fillStyle = '#fff';  // White text for better readability
        ctx.textAlign = 'left';
        ctx.fillText(item.label, currentX + 18, legendY + 3);
        
        currentX += itemWidth;
    });
}

// Function to apply color coding to rank values
function applyRankColors() {
    const rankCells = document.querySelectorAll('.rank-value');
    rankCells.forEach(cell => {
        const value = parseInt(cell.textContent);
        if (!isNaN(value)) {
            if (value <= 5) {
                cell.classList.add('rank-top5');
            } else if (value <= 10) {
                cell.classList.add('rank-top10');
            } else if (value <= 15) {
                cell.classList.add('rank-top15');
            }
        }
    });
}

// Draw charts when page loads
window.addEventListener('load', function() {
    // Apply color coding to ranks
    applyRankColors();
    
    // Draw charts
    drawRankingsChart('awayRankingsChart', '{{ data.away_team.abbreviation }}', '{{ data.away_team.colors.primary }}');
    drawRankingsChart('homeRankingsChart', '{{ data.home_team.abbreviation }}', '{{ data.home_team.colors.primary }}');
});
</script>

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
    from src.data.collectors.team_stats import TeamStatsCollector
    from src.data.collectors.rolling_stats import RollingStatsCollector
    
    # Initialize collectors
    header_collector = GameHeaderCollector()
    stats_collector = TeamStatsCollector()
    rolling_collector = RollingStatsCollector()
    
    # Set game parameters
    away_team = 'MIL'
    home_team = 'PHI'
    game_date = '20250119'
    
    print(f"\n🏀 Generating matchup report for {away_team} @ {home_team}")
    print(f"   Game Date: {game_date}")
    print("-" * 50)
    
    # Collect all data
    print("\n📊 Collecting data...")
    header_data = header_collector.collect(away_team, home_team, game_date)
    stats_data = stats_collector.collect(away_team, home_team, game_date)
    rolling_data = rolling_collector.collect(away_team, home_team, game_date)
    
    # Combine all data
    combined_data = {**header_data, **stats_data, **rolling_data}
    
    # Generate report
    print("\n📝 Generating HTML report...")
    generator = MatchupReportGenerator()
    report_path = generator.generate_report(combined_data)
    
    print(f"\n✅ Report generated successfully!")
    print(f"📂 Location: {report_path}")
    print(f"🌐 Open in browser: file://{report_path.absolute()}")