import requests
import csv

team_id = "63848a2a-fa4d-4532-bacc-d6f3866312d2"
season_id = "1b6142ab-2661-4649-af5f-d26cb5b093b4"

# Player IDs to track
player_ids = {
    "80fadfc7-bd96-4822-bf00-0a3a803f7336": None,
    "80847d06-9926-4556-8caa-855bfa250476": None,
    "b03d245e-7b27-4ef8-9414-7dde159fcc39": None,
    "9c1cd671-8ad4-4d48-9d2d-36c18930498c": None,
    "e27b2669-0349-408f-a609-4aa9ff54d046": None,
    "0e09ded7-398b-4d1e-a2ab-9f8229f5ac02": None,
    "c490b421-6ed0-463a-89ec-07bb846633a2": None,
    "f2e53c28-a88c-4a4a-8a7a-b997d87ce826": None,
    "e6f1ee63-5a8d-4cbc-8805-5505d59dd8ce": None,
    "2dbb8e37-0020-4a3e-b4cb-800714b0aede": None,
    "18cfa220-45b6-4ed2-bd70-91aa78d723e3": None,
    "de7dbcbe-974a-4a65-90b6-c5b3c9c7242f": None,
    "7dcf03c2-c8fb-43f4-a27e-b15b20c474ea": None,
    "293351af-d451-43e0-b3b4-7c417b283cdf": None,
    "2815747f-6c76-4305-b248-b1d68ca4577b": None
}

# API Endpoint for Team Games
games_api = f"https://api.itsovertime.com/api/ote_teams/v1/public/{team_id}/ote_games?status=completed"

response = requests.get(games_api)
if response.status_code != 200:
    print(f"Error fetching games: {response.status_code}")
    exit()

games_data = response.json().get("ote_games", [])

# Dictionaries to store stats
win_stats = {player_id: [] for player_id in player_ids}
loss_stats = {player_id: [] for player_id in player_ids}
win_gp = {player_id: 0 for player_id in player_ids}
loss_gp = {player_id: 0 for player_id in player_ids}

# Process games
for game in games_data:
    if game.get("ote_season_id") != season_id:
        continue

    game_id = game["id"]
    game_result = None

    for team in game["ote_games_ote_teams"]:
        if team["ote_team_id"] == team_id:
            game_result = team["result"]
            break

    if game_result not in ["win", "lose"]:
        continue

    game_stats_api = f"https://api.itsovertime.com/api/ote_games/v1/public/{game_id}/ote_games_ote_players_ote_teams"
    stats_response = requests.get(game_stats_api)
    if stats_response.status_code != 200:
        print(f"Error fetching stats for Game ID {game_id}")
        continue

    game_stats = stats_response.json().get("ote_games_ote_players_ote_teams", [])

    for player_stat in game_stats:
        player_id = player_stat["ote_player_id"]
        if player_id not in player_ids:
            continue

        # Store player name
        player_full_name = player_stat["ote_player"]["full_name"]
        player_ids[player_id] = player_full_name

        stats = {
            "PTS": player_stat.get("points", 0) or 0,
            "ORB": player_stat.get("rebounds_offensive", 0) or 0,
            "DRB": player_stat.get("rebounds_defensive", 0) or 0,
            "TRB": player_stat.get("rebounds_total", 0) or 0,
            "AST": player_stat.get("assists", 0) or 0,
            "TO": player_stat.get("turnovers", 0) or 0,
            "STL": player_stat.get("steals", 0) or 0,
            "BLK": player_stat.get("blocks", 0) or 0,
            "PF": player_stat.get("fouls_personal", 0) or 0,
            "FD": player_stat.get("fouls_drawn", 0) or 0,
            "2PM": player_stat.get("points_two_made", 0) or 0,
            "2PA": player_stat.get("points_two_attempted", 0) or 0,
            "3PM": player_stat.get("points_three_made", 0) or 0,
            "3PA": player_stat.get("points_three_attempted", 0) or 0,
            "FGM": player_stat.get("field_goals_made", 0) or 0,
            "FGA": player_stat.get("field_goals_attempted", 0) or 0,
            "FTM": player_stat.get("free_throws_made", 0) or 0,
            "FTA": player_stat.get("free_throws_attempted", 0) or 0,
            "+/-": player_stat.get("plus_minus", 0) or 0,
        }

        if game_result == "win":
            win_stats[player_id].append(stats)
            win_gp[player_id] += 1
        else:
            loss_stats[player_id].append(stats)
            loss_gp[player_id] += 1

# Correct calculation function
def calculate_averages(stats_list, games_played):
    if not stats_list or games_played == 0:
        return {key: 0 for key in stats_list[0]} if stats_list else {}

    totals = {key: sum(d.get(key, 0) or 0 for d in stats_list) for key in stats_list[0]}

    avg_stats = {key: round(total / games_played, 1) for key, total in totals.items()}

    def safe_div(numerator, denominator):
        return round((numerator / denominator) * 100, 1) if denominator else 0

    avg_stats["FT%"] = safe_div(totals.get("FTM", 0), totals.get("FTA", 0))
    avg_stats["FG%"] = safe_div(totals.get("FGM", 0), totals.get("FGA", 0))
    avg_stats["3P%"] = safe_div(totals.get("3PM", 0), totals.get("3PA", 0))
    avg_stats["2P%"] = safe_div(totals.get("2PM", 0), totals.get("2PA", 0))

    return avg_stats

# Compute averages
win_averages = []
loss_averages = []

for player_id, stats in win_stats.items():
    if not stats:
        continue
    averages = calculate_averages(stats, win_gp[player_id])
    win_averages.append({"Player": player_ids[player_id], "GP": win_gp[player_id], **averages})

for player_id, stats in loss_stats.items():
    if not stats:
        continue
    averages = calculate_averages(stats, loss_gp[player_id])
    loss_averages.append({"Player": player_ids[player_id], "GP": loss_gp[player_id], **averages})

# Sort by Player name
win_averages.sort(key=lambda x: x["Player"])
loss_averages.sort(key=lambda x: x["Player"])

# Use your desired column order
csv_headers = [
    "Player", "GP", "PTS", "ORB", "DRB", "TRB", "AST", "TO", "STL", "BLK", "PF", "FD",
    "2PM", "2PA", "2P%", "3PM", "3PA", "3P%", "FGM", "FGA", "FG%", "FTM", "FTA", "FT%", "+/-"
]

# Write Win Splits
with open("win_splits.csv", mode="w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()
    writer.writerows(win_averages)

# Write Loss Splits
with open("loss_splits.csv", mode="w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()
    writer.writerows(loss_averages)

print(f"✅ Win splits saved to win_splits.csv")
print(f"✅ Loss splits saved to loss_splits.csv")
