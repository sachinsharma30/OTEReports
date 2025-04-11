import requests
import csv

# === Player IDs ===
player_ids = [
    "7354d7f6-6d3d-43ba-a277-bca4a2d9c079",
    "f75d3a0f-7519-4fad-bebb-8abba059f5dd",
    "1dacc2fd-244d-4304-9709-95254e1e64b8",
    "4d6cb7ed-6003-45ee-8ad9-3be069e1e03f",
    "4f251186-6a90-4b99-ac97-6146f9fe56b5",
    "44409d12-0024-4015-adbe-245737a74251",
    "a45ed6cc-d64a-4caf-a439-76cb1edc8184",
    "84266f82-3931-4e29-b33a-0ae1ce41c75c",
    "2c9b4e9d-a810-48c4-98c8-fca8bb18f335",
    "7a78e97d-42ad-49d1-ac3a-ed4f4174b8ef",
    "ab024e75-65cf-4336-bb69-d335c9309134",
    "100b690e-bef8-4c17-9579-f48b024ba39b",
    "f967cb86-5fad-4d97-b6ac-5e63810585e9",
    "b1574287-9d22-470a-a3d9-ba37640a2a98",
    "d98c65a8-9684-4624-8c14-1761b60f5112",
    "2253748e-dbf1-4385-8a83-0aa53358df4a",
    "4589b12c-fb0c-400f-ac53-b650072442a5",
    "822a7812-b84e-4910-aabe-dea743e5a2ae",
    "b9e9ec9f-dd0c-424f-9cfb-d90ed6a5e57e",
    "4fd16dfc-21b9-459f-b6dd-a92ac8b6a378",
    "5de8b67d-9805-416d-968e-8e3a8fa1eae2",
    "0c394521-208a-47fb-97cd-366f7db2ad35",
    "b2fa7abc-caeb-4a7c-ab80-9f97e5a14f3e",
    "c6ee3d78-e81e-4432-8f19-bd51b2e6c9c4",
    "2f762405-b98f-414d-a026-e6a21d17c76b",
    "686cf670-0db8-4c41-a1a1-ee65565862c3",
    "030d3994-f561-4421-b946-84ab64bfdbca",
    "6bce1a58-1633-475d-88a3-2f65b22d13b1"
]

# === Seasons mapping ===
seasons = {
    "2024-2025": "1b6142ab-2661-4649-af5f-d26cb5b093b4",
    "2023-2024": "de408682-41f0-4c2a-b3f7-53ee62b9ef4a",
    "2022-2023": "e130bb01-9005-4690-83e6-320eec091f1f"
}

csv_filename = "player_per40.csv"

# === Headers with Season ===
csv_headers = [
    "Season", "Name", "GP", "MIN", "PTS", "ORB", "DRB", "TRB", "AST", "TO", "STL", "BLK", "PF", "FD",
    "2PM", "2PA", "2P%", "3PM", "3PA", "3P%", "FGM", "FGA", "FG%", "FTM", "FTA", "FT%", "+/-"
]

# === Helpers ===
def per_40(value, minutes):
    if not minutes or minutes == 0:
        return None
    return f"{(float(value) * 40 / minutes):.1f}"

def format_percent(value):
    if value is None:
        return None
    return f"{float(value):.1f}%"

# === Collect all rows ===
all_rows = []

for player_id in player_ids:
    api_url = f"https://api.itsovertime.com/api/ote_players/v1/public/{player_id}"
    response = requests.get(api_url)

    if response.status_code != 200:
        print(f"❌ Error fetching data for {player_id}: {response.status_code}")
        continue

    data = response.json()
    player = data.get("ote_player", {})
    player_name = player.get("full_name", "Unknown Player")

    for season_name, season_id in seasons.items():
        season_stats = None
        for season in player.get("ote_seasons_ote_players", []):
            if season.get("ote_season_id") == season_id:
                season_stats = season
                break

        games_played = season_stats.get("games", 0) if season_stats else 0
        total_minutes = season_stats.get("minutes", 0) if season_stats else 0

        if not season_stats or games_played == 0 or total_minutes == 0:
            continue  # Skip empty or zero-minute seasons

        row_data = [
            season_name,
            player_name,
            str(games_played),
            "40.0",  # Per 40 min constant
            per_40(season_stats.get("points", 0), total_minutes),
            per_40(season_stats.get("rebounds_offensive", 0), total_minutes),
            per_40(season_stats.get("rebounds_defensive", 0), total_minutes),
            per_40(season_stats.get("rebounds_total", 0), total_minutes),
            per_40(season_stats.get("assists", 0), total_minutes),
            per_40(season_stats.get("turnovers", 0), total_minutes),
            per_40(season_stats.get("steals", 0), total_minutes),
            per_40(season_stats.get("blocks", 0), total_minutes),
            per_40(season_stats.get("fouls_personal", 0), total_minutes),
            per_40(season_stats.get("fouls_drawn", 0), total_minutes),
            per_40(season_stats.get("points_two_made", 0), total_minutes),
            per_40(season_stats.get("points_two_attempted", 0), total_minutes),
            format_percent(season_stats.get("points_two_percentage", 0.0)),
            per_40(season_stats.get("points_three_made", 0), total_minutes),
            per_40(season_stats.get("points_three_attempted", 0), total_minutes),
            format_percent(season_stats.get("points_three_percentage", 0.0)),
            per_40(season_stats.get("field_goals_made", 0), total_minutes),
            per_40(season_stats.get("field_goals_attempted", 0), total_minutes),
            format_percent(season_stats.get("field_goals_percentage", 0.0)),
            per_40(season_stats.get("free_throws_made", 0), total_minutes),
            per_40(season_stats.get("free_throws_attempted", 0), total_minutes),
            format_percent(season_stats.get("free_throws_percentage", 0.0)),
            per_40(season_stats.get("plus_minus", 0), total_minutes),
        ]

        all_rows.append(row_data)

# Sort rows by Player Name then Season
all_rows.sort(key=lambda x: (x[1], x[0]))

# === Write to CSV ===
with open(csv_filename, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(csv_headers)
    writer.writerows(all_rows)

print(f"✅ Player per 40-minute averages saved to `{csv_filename}` successfully!")
