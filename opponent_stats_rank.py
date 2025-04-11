import requests
import pandas as pd

# Team IDs
teams = {
    "Jelly Fam": "bc8b7fd0-4fd7-4559-bd03-6939cf8d158d",
    "Blue Checks": "e66d33bb-cdc2-4e29-92d6-7beb51416a0e",
    "Diamond Doves": "951ee7b6-568e-4bf7-b9f7-72390e72cbac",
    "Cold Hearts": "311c9f05-3daa-4739-8111-db97053e4971",
    "RWE": "2823e631-2735-46f7-b8f9-4250f6e9e0f5",
    "City Reapers": "6b0dab6a-71ed-4234-ac93-5a964b90cfd8",
    "YNG Dreamerz": "3ad6ec4a-dd8a-466c-8f1a-c6846ae1e7c6",
    "Fear of God Athletics": "63848a2a-fa4d-4532-bacc-d6f3866312d2",
}

season_id = "1b6142ab-2661-4649-af5f-d26cb5b093b4"

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

# Stats container
opponent_averages = {}

# Fetch opponent stats
for team_name, team_id in teams.items():
    url = f"https://api.itsovertime.com/api/ote_teams/v1/public/{team_id}/ote_games?status=completed"
    res = requests.get(url)
    if res.status_code != 200:
        print(f"Failed to fetch for {team_name}")
        continue

    games = res.json().get("ote_games", [])
    totals = {k: 0 for k in stat_categories}
    game_count = 0

    for game in games:
        if game.get("ote_season_id") != season_id:
            continue
        for g_team in game.get("ote_games_ote_teams", []):
            if g_team.get("ote_team", {}).get("id") != team_id:
                if g_team.get("score", 0) == 0:
                    continue
                for k, v in stat_categories.items():
                    val = g_team.get(v)
                    if isinstance(val, (int, float)):
                        totals[k] += val
                game_count += 1

    if game_count:
        opponent_averages[team_name] = {
            k: round(totals[k] / game_count, 2) for k in stat_categories
        }

# DataFrame
df = pd.DataFrame.from_dict(opponent_averages, orient="index")

# Ordinal formatting
def ordinal(n):
    return f"{n}{'tsnrhtdd'[(n//10%10!=1)*(n%10<4)*n%10::4]}"

# Rank formatting
ranked_df = df.copy()
for col in df.columns:
    # Descending rank for TO and PF
    ascending = False if col in ["TO", "PF"] else True
    ranked_df[col] = df[col].rank(ascending=ascending, method="min").astype(int)
    ranked_df[col] = ranked_df[col].apply(ordinal)

# Save to CSV
ranked_df.to_csv("opponent_stat_rankings.csv")
print("✅ Opponent stat rankings saved to 'opponent_stat_rankings.csv'")
