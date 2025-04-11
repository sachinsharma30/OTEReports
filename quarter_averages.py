import requests
import csv

# Define Team ID and Season ID
TEAM_ID = "63848a2a-fa4d-4532-bacc-d6f3866312d2"
SEASON_ID = "1b6142ab-2661-4649-af5f-d26cb5b093b4"

# API Endpoint to get completed games
games_api = f"https://api.itsovertime.com/api/ote_teams/v1/public/{TEAM_ID}/ote_games?status=completed"

# Fetch all game IDs for the specified team and season
response = requests.get(games_api)
if response.status_code != 200:
    print(f"Error fetching games: {response.status_code}")
    exit()

games_data = response.json().get("ote_games", [])
game_ids = [game["id"] for game in games_data if game.get("ote_season_id") == SEASON_ID]

# Data structure to store quarter stats
quarter_stats = {1: [], 2: [], 3: [], 4: []}

# Fetch and process stats for each game
for game_id in game_ids:
    period_stats_api = f"https://api.itsovertime.com/api/ote_games_ote_teams_periods/v1/public/{game_id}"
    stats_response = requests.get(period_stats_api)

    if stats_response.status_code != 200:
        print(f"Error fetching stats for Game ID {game_id}")
        continue

    periods_data = stats_response.json().get("ote_games_ote_teams_periods", [])

    # Process period stats for our team
    for period_stat in periods_data:
        period_id = period_stat["period_id"]
        team_id = period_stat["ote_game_ote_team"]["ote_team_id"]
        points = period_stat.get("points", 0)

        # Store stats only if it's our team
        if team_id == TEAM_ID and period_id in quarter_stats:
            quarter_stats[period_id].append({
                "PTS": points,
                "ORB": period_stat.get("rebounds_offensive", 0),
                "DRB": period_stat.get("rebounds_defensive", 0),
                "TRB": period_stat.get("rebounds_total", 0),
                "AST": period_stat.get("assists", 0),
                "TO": period_stat.get("turnovers", 0),
                "STL": period_stat.get("steals", 0),
                "BLK": period_stat.get("blocks", 0),
                "PF": period_stat.get("fouls_personal", 0),
                "FD": period_stat.get("fouls_drawn", 0),
                "2PM": period_stat.get("points_two_made", 0),
                "2PA": period_stat.get("points_two_attempted", 0),
                "3PM": period_stat.get("points_three_made", 0),
                "3PA": period_stat.get("points_three_attempted", 0),
                "FGM": period_stat.get("field_goals_made", 0),
                "FGA": period_stat.get("field_goals_attempted", 0),
                "FTM": period_stat.get("free_throws_made", 0),
                "FTA": period_stat.get("free_throws_attempted", 0),
            })

# Function to compute average values for each quarter
def compute_quarter_averages(stats_list):
    if not stats_list:
        return {
            "PTS": 0, "ORB": 0, "DRB": 0, "TRB": 0, "AST": 0, "TO": 0, "STL": 0, "BLK": 0, "PF": 0, "FD": 0,
            "2PM": 0, "2PA": 0, "3PM": 0, "3PA": 0, "FGM": 0, "FGA": 0, "FTM": 0, "FTA": 0,
            "2P%": 0, "3P%": 0, "FG%": 0, "FT%": 0
        }

    totals = {key: sum(d[key] for d in stats_list) for key in stats_list[0]}
    num_games = len(stats_list)

    averages = {key: round(totals[key] / num_games, 2) for key in totals}

    # Calculate shooting percentages from totals
    averages["2P%"] = round(totals["2PM"] / totals["2PA"] * 100, 2) if totals["2PA"] else 0
    averages["3P%"] = round(totals["3PM"] / totals["3PA"] * 100, 2) if totals["3PA"] else 0
    averages["FG%"] = round(totals["FGM"] / totals["FGA"] * 100, 2) if totals["FGA"] else 0
    averages["FT%"] = round(totals["FTM"] / totals["FTA"] * 100, 2) if totals["FTA"] else 0

    return averages

# Compute averages for each quarter
quarter_averages = {
    "Q1 Avg": compute_quarter_averages(quarter_stats[1]),
    "Q2 Avg": compute_quarter_averages(quarter_stats[2]),
    "Q3 Avg": compute_quarter_averages(quarter_stats[3]),
    "Q4 Avg": compute_quarter_averages(quarter_stats[4]),
}

# CSV File Output
csv_filename = "quarter_averages.csv"
csv_headers = ["Team", "PTS", "ORB", "DRB", "TRB", "AST", "TO", "STL", "BLK", "PF", "FD",
               "2PM", "2PA", "2P%", "3PM", "3PA", "3P%", "FGM", "FGA", "FG%", "FTM", "FTA", "FT%"]

with open(csv_filename, mode="w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()

    for quarter, stats in quarter_averages.items():
        writer.writerow({"Team": quarter, **stats})

print(f"✅ Quarter averages saved to {csv_filename}")
