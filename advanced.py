import requests
import csv

# === Constants ===
players = [
    {"name": "Jeremiah Faumuina", "id": "7354d7f6-6d3d-43ba-a277-bca4a2d9c079"},
    {"name": "Amari Evans", "id": "1dacc2fd-244d-4304-9709-95254e1e64b8"},
    {"name": "Samis Calderon", "id": "84266f82-3931-4e29-b33a-0ae1ce41c75c"},
    {"name": "Romelo Hill", "id": "7a78e97d-42ad-49d1-ac3a-ed4f4174b8ef"},
    {"name": "Adam Oumiddoch", "id": "b1574287-9d22-470a-a3d9-ba37640a2a98"},
    {"name": "Jayden Wilkins", "id": "822a7812-b84e-4910-aabe-dea743e5a2ae"},
    {"name": "Parker Robinson", "id": "0c394521-208a-47fb-97cd-366f7db2ad35"},
]

seasons = {
    "2023-2024": "de408682-41f0-4c2a-b3f7-53ee62b9ef4a",
    "2022-2023": "e130bb01-9005-4690-83e6-320eec091f1f"
}

# Opponent constants
opponent_stats = {
    "ORB": 15.0,
    "DRB": 26.5,
    "FGA": 70.6,
    "3PA": 26.6
}

# === Helpers ===
def safe_float(value):
    try:
        return float(value) if value is not None else 0.0
    except:
        return 0.0

def get_json(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"⚠️ Failed to fetch {url}")
        return {}

# === Prepare output CSV ===
output_file = "advanced_metrics.csv"
csv_headers = ["Season", "Player", "TSA", "TS%", "3PAr", "FTAr", "AST%", "TO%", "ORB%", "DRB%", "STL%", "BLK%"]

with open(output_file, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(csv_headers)

    # === Process each player & season ===
    for player in players:
        player_name = player["name"]
        player_id = player["id"]

        for season_name, season_id in seasons.items():
            print(f"Processing {player_name} - {season_name}")

            # === Get player season averages ===
            player_url = f"https://api.itsovertime.com/api/ote_seasons/v1/public/{season_id}/ote_seasons_ote_players"
            player_data = get_json(player_url).get("ote_seasons_ote_players", [])

            player_stats = next((p for p in player_data if p.get("ote_player_id") == player_id), None)
            if not player_stats:
                print(f"⏭️ No player data for {player_name} in {season_name}")
                continue

            # === Get game list (correct endpoint) ===
            games_url = f"https://api.itsovertime.com/api/ote_seasons/v1/public/{season_id}/ote_games?ote_player_id={player_id}"
            games_data = get_json(games_url).get("ote_games", [])

            if not games_data:
                print(f"⏭️ No games found for {player_name} in {season_name}")
                continue

            # === Collect team stats from games ===
            total_fgm = total_orb = total_drb = 0
            team_game_count = 0

            for game in games_data:
                teams = game.get("ote_games_ote_teams", [])
                if not teams:
                    continue

                for team in teams:
                    total_fgm += safe_float(team.get("field_goals_made"))
                    total_orb += safe_float(team.get("rebounds_offensive"))
                    total_drb += safe_float(team.get("rebounds_defensive"))

                team_game_count += 1

            if team_game_count == 0:
                print(f"⏭️ No team data for {player_name} in {season_name}")
                continue

            # === Calculate team averages ===
            team_stats = {
                "FGM": total_fgm / (team_game_count * 2),  # both teams per game
                "ORB": total_orb / (team_game_count * 2),
                "DRB": total_drb / (team_game_count * 2)
            }

            # === Player stats ===
            PTS = safe_float(player_stats.get("points_per_game"))
            FGA = safe_float(player_stats.get("field_goals_attempted_per_game"))
            FTA = safe_float(player_stats.get("free_throws_attempted_per_game"))
            FGM = safe_float(player_stats.get("field_goals_made_per_game"))
            FG3A = safe_float(player_stats.get("three_pointers_attempted_per_game"))
            AST = safe_float(player_stats.get("assists_per_game"))
            TOV = safe_float(player_stats.get("turnovers_per_game"))
            ORB = safe_float(player_stats.get("rebounds_offensive_per_game"))
            DRB = safe_float(player_stats.get("rebounds_defensive_per_game"))
            STL = safe_float(player_stats.get("steals_per_game"))
            BLK = safe_float(player_stats.get("blocks_per_game"))
            MP = safe_float(player_stats.get("minutes_per_game"))

            # === Calculations ===
            TSA = round(FGA + 0.44 * FTA, 1)
            TS_percent = round(PTS / (2 * TSA) * 100, 1) if TSA else 0
            threepar = round(100 * FG3A / FGA, 1) if FGA else 0
            ftar = round(100 * FTA / FGA, 1) if FGA else 0
            ast_percent = round(100 * AST / (((MP / 36) * team_stats["FGM"]) - FGM), 1) if MP and (((MP / 36) * team_stats["FGM"]) - FGM) else 0
            to_percent = round(100 * TOV / (FGA + 0.44 * FTA + TOV), 1) if (FGA + 0.44 * FTA + TOV) else 0
            orb_percent = round(100 * ORB * 36 / (MP * (team_stats["ORB"] + opponent_stats["DRB"])), 1) if MP else 0
            drb_percent = round(100 * DRB * 36 / (MP * (team_stats["DRB"] + opponent_stats["ORB"])), 1) if MP else 0
            stl_percent = round(100 * STL * 36 / (MP * 75.26), 1) if MP else 0
            blk_percent = round(100 * BLK * 36 / (MP * (opponent_stats["FGA"] - opponent_stats["3PA"])), 1) if MP else 0

            # ✅ Write to CSV in correct order
            writer.writerow([
                season_name,
                player_name,
                TSA,
                TS_percent,
                threepar,
                ftar,
                ast_percent,
                to_percent,
                orb_percent,
                drb_percent,
                stl_percent,
                blk_percent
            ])

print(f"✅ Done! Advanced metrics saved to {output_file}")
