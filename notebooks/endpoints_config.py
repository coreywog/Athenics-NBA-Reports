"""
MySportsFeeds API Endpoint Configurations
Complete list of all available endpoints with their parameters
"""

ENDPOINTS = {
    "CORE": {
        "current_season": {
            "path": "/current_season",
            "description": "Returns current season and supported stats",
            "params": {
                "date": "optional",  # specify a date
                "force": "optional"  # force-if-not-modified
            }
        },
        "latest_updates": {
            "path": "/{season}/latest_updates",
            "description": "Lists all latest update timestamps for each feed",
            "params": {
                "force": "optional"
            }
        },
        "seasonal_venues": {
            "path": "/{season}/venues",
            "description": "Lists all venues used in the season",
            "params": {
                "team": "optional",  # list-of-teams
                "force": "optional"
            }
        },
        "daily_games": {
            "path": "/{season}/date/{date}/games",
            "description": "All games on a given date with schedule, status and scores",
            "params": {
                "team": "optional",  # list-of-teams
                "status": "optional",  # list-of-game-statuses
                "sort": "optional",
                "offset": "optional",
                "limit": "optional",
                "force": "optional"
            }
        },
        "seasonal_games": {
            "path": "/{season}/games",
            "description": "All games for a season including schedule, status and scores",
            "params": {
                "team": "optional",
                "date": "optional",  # date-range
                "status": "optional",
                "sort": "optional",
                "offset": "optional",
                "limit": "optional",
                "force": "optional"
            }
        }
    },
    
    "STATS": {
        "seasonal_team_stats": {
            "path": "/{season}/team_stats_totals",
            "description": "Each team with their seasonal stats totals",
            "params": {
                "team": "optional",
                "date": "optional",  # date-range
                "stats": "optional",  # list-of-stats
                "sort": "optional",
                "offset": "optional",
                "limit": "optional",
                "force": "optional"
            }
        },
        "seasonal_player_stats": {
            "path": "/{season}/player_stats_totals",
            "description": "Each player with their seasonal stats totals",
            "params": {
                "player": "optional",
                "position": "optional",
                "country": "optional",
                "team": "optional",
                "date": "optional",
                "stats": "optional",
                "sort": "optional",
                "offset": "optional",
                "limit": "optional",
                "force": "optional"
            }
        },
        "daily_team_gamelogs": {
            "path": "/{season}/date/{date}/team_gamelogs",
            "description": "All team game logs for a date including game and stats",
            "params": {
                "team": "optional",
                "game": "optional",
                "stats": "optional",
                "sort": "optional",
                "offset": "optional",
                "limit": "optional",
                "force": "optional"
            }
        },
        "daily_player_gamelogs": {
            "path": "/{season}/date/{date}/player_gamelogs",
            "description": "All player game logs for a date including game and stats",
            "params": {
                "team": "optional",
                "player": "optional",
                "position": "optional",
                "game": "optional",
                "stats": "optional",
                "sort": "optional",
                "offset": "optional",
                "limit": "optional",
                "force": "optional"
            }
        },
        "seasonal_standings": {
            "path": "/{season}/standings",
            "description": "All teams with their stats and rankings",
            "params": {
                "date": "optional",
                "team": "optional",
                "stats": "optional",
                "force": "optional"
            }
        }
    },
    
    "DETAILED": {
        "game_boxscore": {
            "path": "/{season}/games/{game}/boxscore",
            "description": "Boxscore for a game including game details and team/player stats",
            "params": {
                "teamstats": "optional",
                "playerstats": "optional",
                "sort": "optional",
                "offset": "optional",
                "limit": "optional",
                "force": "optional"
            }
        },
        "game_lineup": {
            "path": "/{season}/games/{game}/lineup",
            "description": "Expected and actual lineup for a game",
            "params": {
                "position": "optional",
                "lineuptype": "optional",
                "force": "optional"
            }
        },
        "game_playbyplay": {
            "path": "/{season}/games/{game}/playbyplay",
            "description": "All play-by-play events for a game with full details",
            "params": {
                "playtype": "optional",
                "sort": "optional",
                "offset": "optional",
                "limit": "optional",
                "force": "optional"
            }
        },
        "players": {
            "path": "/players",
            "description": "All players with full bio and details",
            "params": {
                "season": "optional",
                "date": "optional",
                "team": "optional",
                "rosterstatus": "optional",
                "player": "optional",
                "position": "optional",
                "country": "optional",
                "sort": "optional",
                "offset": "optional",
                "limit": "optional",
                "force": "optional"
            }
        },
        "injuries": {
            "path": "/injuries",
            "description": "List of all currently injured players",
            "params": {
                "player": "optional",
                "team": "optional",
                "position": "optional",
                "sort": "optional",
                "offset": "optional",
                "limit": "optional",
                "force": "optional"
            }
        },
        "injury_history": {
            "path": "/injury_history",
            "description": "Injury history for all players",
            "params": {
                "season": "optional",
                "date": "optional",
                "team": "optional",
                "player": "optional",
                "position": "optional",
                "force": "optional"
            }
        }
    }
}

# Test data for examples
TEST_DATA = {
    "season": "2024-2025-regular",
    "date": "20241023",  # October 23, 2024
    "date_range": "from-20241020-to-20241027",
    "game": "20241023-MIL-PHI",
    "teams": ["MIL", "PHI", "LAL", "GSW", "BOS"],
    "players": {
        "MIL": ["giannis-antetokounmpo", "damian-lillard"],
        "PHI": ["joel-embiid", "tyrese-maxey"],
        "LAL": ["lebron-james", "anthony-davis"],
        "GSW": ["stephen-curry", "klay-thompson"],
        "BOS": ["jayson-tatum", "jaylen-brown"]
    }
}

# Common stats to request
COMMON_STATS = {
    "team": [
        "W", "L", "PTS", "AST", "REB", "STL", "BLK", "TOV", 
        "FG%", "3P%", "FT%", "OREB", "DREB"
    ],
    "player": [
        "PTS", "AST", "REB", "STL", "BLK", "TOV", "MIN",
        "FGM", "FGA", "FG%", "3PM", "3PA", "3P%", "FTM", "FTA", "FT%"
    ]
}