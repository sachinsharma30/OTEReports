import requests
import csv

# Define Season ID and Team IDs
SEASON_ID = "1b6142ab-2661-4649-af5f-d26cb5b093b4"
TEAM_IDS = {
    "Jelly Fam": "bc8b7fd0-4fd7-4559-bd03-6939cf8d158d",
    "Blue Checks": "e66d33bb-cdc2-4e29-92d6-7beb51416a0e",
    "Diamond Doves": "951ee7b6-568e-4bf7-b9f7-72390e72cbac",
    "Cold Hearts": "311c9f05-3daa-4739-8111-db97053e4971",
    "RWE": "2823e631-2735-46f7-b8f9-4250f6e9e0f5",
    "City Reapers": "6b0dab6a-71ed-4234-ac93-5a964b90cfd8",
    "YNG Dreamerz": "3ad6ec4a-dd8a-466c-8f1a-c6846ae1e7c6",
    "Fear of God Athletics": "63848a2a-fa4d-4532-bacc-d6f3866312d2",
}
SPECIFIED_TEAM = "Fear of God Athletics"

# Function to add ordinal suffix to numbers (1st, 2nd, 3rd, etc.)
def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"

# Data structure to store quarter stats per team
team_quarter_stats = {team: {1: [], 2: [], 3: [], 4: []} for team in TEAM_IDS}

# Fetch data for all teams
for team_name, team_id in TEAM_IDS.items():
    print(f"Fetching data for {team_name}...")

    games_api = f"https://api.itsovertime.com/api/ote_teams/v1/public/{team_id}/ote_games?status=completed"
    response = requests.get(games_api)
    if response.status_code != 200:
        print(f"Error fetching games for {team_name}: {response.status_code}")
        continue

    games_data = response.json().get("ote_games", [])
    game_ids = [game["id"] for game in games_data if game.get("ote_season_id") == SEASON_ID]

    # Process each game
    for game_id in game_ids:
        period_stats_api = f"https://api.itsovertime.com/api/ote_games_ote_teams_periods/v1/public/{game_id}"
        stats_response = requests.get(period_stats_api)

        if stats_response.status_code != 200:
            print(f"Error fetching stats for Game ID {game_id}")
            continue

        periods_data = stats_response.json().get("ote_games_ote_teams_periods", [])

        # Process period stats for both teams
        for period_stat in periods_data:
            period_id = period_stat["period_id"]
            team_id_stat = period_stat["ote_game_ote_team"]["ote_team_id"]
            points = period_stat.get("points", 0)

            if team_id_stat == team_id and period_id in team_quarter_stats[team_name]:
                team_quarter_stats[team_name][period_id].append({
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

# Function to compute team quarter totals and averages
def compute_team_quarter_averages(stats_list):
    if not stats_list:
        return {key: 0 for key in ["PTS", "ORB", "DRB", "TRB", "AST", "TO", "STL", "BLK", "PF", "FD",
                                  "2PM", "2PA", "3PM", "3PA", "FGM", "FGA", "FTM", "FTA",
                                  "2P%", "3P%", "FG%", "FT%"]}

    totals = {key: sum(d[key] for d in stats_list) for key in stats_list[0]}
    num_games = len(stats_list)

    averages = {key: round(totals[key] / num_games, 2) for key in totals}

    # Calculate shooting percentages from totals
    averages["2P%"] = round(totals["2PM"] / totals["2PA"] * 100, 2) if totals["2PA"] else 0
    averages["3P%"] = round(totals["3PM"] / totals["3PA"] * 100, 2) if totals["3PA"] else 0
    averages["FG%"] = round(totals["FGM"] / totals["FGA"] * 100, 2) if totals["FGA"] else 0
    averages["FT%"] = round(totals["FTM"] / totals["FTA"] * 100, 2) if totals["FTA"] else 0

    return averages

# Compute quarterly averages for all teams
quarterly_averages = {
    team: {q: compute_team_quarter_averages(stats) for q, stats in quarters.items()}
    for team, quarters in team_quarter_stats.items()
}

# Rank teams per quarter for each stat
def rank_teams(quarter, stat_key):
    ranked = sorted(
        TEAM_IDS.keys(),
        key=lambda t: float(quarterly_averages[t][quarter].get(stat_key, 0) or 0),
        reverse=True
    )
    return {team: ordinal(rank + 1) for rank, team in enumerate(ranked)}

# Compute rankings for all quarters
quarterly_rankings = {
    q: {stat: rank_teams(q, stat) for stat in quarterly_averages[SPECIFIED_TEAM][q]}
    for q in range(1, 5)
}

# CSV Output
csv_filename = "quarter_rank.csv"
csv_headers = ["Team", "PTS", "ORB", "DRB", "TRB", "AST", "TO", "STL", "BLK", "PF", "FD",
               "2PM", "2PA", "2P%", "3PM", "3PA", "3P%", "FGM", "FGA", "FG%", "FTM", "FTA", "FT%"]

with open(csv_filename, mode="w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=csv_headers)
    writer.writeheader()

    for quarter, stats in quarterly_rankings.items():
        writer.writerow({"Team": f"Q{quarter} Rank", **{k: stats[k][SPECIFIED_TEAM] for k in stats}})

print(f"✅ Team Quarter Rankings saved to {csv_filename}")
