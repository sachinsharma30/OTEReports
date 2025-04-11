import requests

# Define player and season IDs
player_id = "4589b12c-fb0c-400f-ac53-b650072442a5"
season_id = "1b6142ab-2661-4649-af5f-d26cb5b093b4"
api_url = f"https://api.itsovertime.com/api/ote_players/v1/public/{player_id}"

# Fetch player data (only one API call)
response = requests.get(api_url)
if response.status_code != 200:
    print("Error fetching data:", response.status_code)
    exit()

data = response.json()

# Extract player details
player = data.get("ote_player", {})
player_name = player.get("full_name", "Unknown Player")

# Filter stats for the given season
season_stats = None
for season in player.get("ote_seasons_ote_players", []):
    if season.get("ote_season_id") == season_id:
        season_stats = season
        break

if not season_stats:
    print(f"No stats found for {player_name} in the 2024-2025 Season.")
    exit()

# Define stat categories
categories = {
    "GP": "games",
    "MIN": "minutes",
    "PTS": "points",
    "ORB": "rebounds_offensive",
    "DRB": "rebounds_defensive",
    "TRB": "rebounds_total",
    "AST": "assists",
    "TO": "turnovers",
    "STL": "steals",
    "BLK": "blocks",
    "PF": "fouls_personal",
    "FD": "fouls_drawn",
    "2PM": "two_pointers_made",
    "2PA": "two_pointers_attempted",
    "2P%": "two_pointers_percentage",
    "3PM": "three_pointers_made",
    "3PA": "three_pointers_attempted",
    "3P%": "three_pointers_percentage",
    "FGM": "field_goals_made",
    "FGA": "field_goals_attempted",
    "FG%": "field_goals_percentage",
    "FTM": "free_throws_made",
    "FTA": "free_throws_attempted",
    "FT%": "free_throws_percentage",
    "+/-": "plus_minus",
}

# Define keys for different stat types
totals = categories
per_game = {key: f"{value}_per_game" for key, value in categories.items()}
per_40 = {key: f"{value}_per_40" for key, value in categories.items()}

# Print formatted output
print(f"\nPlayer Stats for {player_name} (2024-2025 Season)")
print("=" * 80)
print(f"{'Stat':<6} | {'Total':<8} | {'Per Game':<10} | {'Per 40 Min':<10}")
print("-" * 80)

for label, key in totals.items():
    total = season_stats.get(key, "N/A")
    per_game_val = season_stats.get(per_game[label], "N/A")
    per_40_val = season_stats.get(per_40[label], "N/A")
    print(f"{label:<6} | {str(total):<8} | {str(per_game_val):<10} | {str(per_40_val):<10}")

print("=" * 80)
