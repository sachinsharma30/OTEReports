import requests
import csv

# Define constants
team_id = "311c9f05-3daa-4739-8111-db97053e4971"  # City Reapers team ID
season_id = "de408682-41f0-4c2a-b3f7-53ee62b9ef4a"  # 2024-2025 Season

# API endpoint for completed games of City Reapers
api_url = f"https://api.itsovertime.com/api/ote_teams/v1/public/{team_id}/ote_games?status=completed"

# Fetch game data
response = requests.get(api_url)
if response.status_code != 200:
    print(f"Error fetching data: {response.status_code}")
    exit()

games = response.json().get("ote_games", [])

# Stats categories
stat_categories = {
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
}

# Initialize totals and game count
opponent_totals = {stat: 0 for stat in stat_categories.keys()}
game_count = 0

# Store individual game records for CSV
game_records = []

# Process games
for game in games:
    if game.get("ote_season_id") != season_id:
        continue  # Skip games from other seasons

    competition_name = game.get("competition_name", "Unknown Competition")
    game_start = game.get("starts_at", "Unknown Start Time")

    for team in game.get("ote_games_ote_teams", []):
        # Ignore City Reapers' own stats
        if team.get("ote_team", {}).get("id") == team_id:
            continue

        opponent_score = team.get("score", 0)
        if opponent_score == 0:
            continue  # Skip invalid games

        print(f"Opponent Score: {opponent_score} | Competition: {competition_name} | Date: {game_start}")
        game_count += 1

        # Store game record for CSV
        game_record = {
            "Opponent Score": opponent_score,
            "Competition Name": competition_name,
            "Game Date": game_start,
        }

        # Aggregate opponent stats
        for label, key in stat_categories.items():
            value = team.get(key, 0)
            if isinstance(value, (int, float)):
                opponent_totals[label] += value
                game_record[label] = value  # Store individual game stats for CSV
            else:
                game_record[label] = "N/A"

        game_records.append(game_record)

# Compute averages
if game_count > 0:
    opponent_averages = {stat: round(total / game_count, 1) for stat, total in opponent_totals.items()}
else:
    opponent_averages = {stat: "N/A" for stat in opponent_totals.keys()}

# Save data to CSV
csv_filename = "city_reapers_opponent_averages.csv"

with open(csv_filename, mode="w", newline="") as file:
    fieldnames = ["Opponent Score", "Competition Name", "Game Date"] + list(stat_categories.keys())
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(game_records)  # Save individual game data

    # Add a separator row
    writer.writerow({})
    # Add overall averages to CSV
    writer.writerow({"Competition Name": "Opponent Season Averages", **opponent_averages})

print(f"\nOpponent stats saved to {csv_filename}")
