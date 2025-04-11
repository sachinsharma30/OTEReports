import requests

# === Setup ===
season_ids = {
    "2023-2024": "de408682-41f0-4c2a-b3f7-53ee62b9ef4a",
    "2022-2023": "e130bb01-9005-4690-83e6-320eec091f1f"
}

players = {
    "Jeremiah Faumuina": "7354d7f6-6d3d-43ba-a277-bca4a2d9c079",
    "Amari Evans": "1dacc2fd-244d-4304-9709-95254e1e64b8",
    "Samis Calderon": "84266f82-3931-4e29-b33a-0ae1ce41c75c",
    "Romelo Hill": "7a78e97d-42ad-49d1-ac3a-ed4f4174b8ef",
    "Adam Oumiddoch": "b1574287-9d22-470a-a3d9-ba37640a2a98",
    "Jayden Wilkins": "822a7812-b84e-4910-aabe-dea743e5a2ae",
    "Parker Robinson": "0c394521-208a-47fb-97cd-366f7db2ad35",
}

stats_to_avg = ["field_goals_made", "rebounds_offensive", "rebounds_defensive"]

# === Go through players and seasons ===
for player_name, player_id in players.items():
    for season_name, season_id in season_ids.items():
        print(f"\n📊 {player_name} - {season_name}")

        # Prepare accumulators
        totals = {stat: 0 for stat in stats_to_avg}
        game_count = 0

        # Get games this player played in this season
        url = f"https://api.itsovertime.com/api/ote_seasons/v1/public/{season_id}/ote_games?ote_player_id={player_id}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Failed to fetch games for {player_name} in {season_name}")
            continue

        games = response.json().get("ote_games", [])
        if not games:
            print(f"⚠️ No games found for {player_name} in {season_name}")
            continue

        for game in games:
            teams = game.get("ote_games_ote_teams", [])
            if not teams:
                continue

            for team in teams:
                for stat in stats_to_avg:
                    value = team.get(stat)
                    if value is not None:
                        totals[stat] += float(value)

            game_count += 1

        if game_count > 0:
            print(f"✅ Games counted: {game_count}")
            for stat in stats_to_avg:
                avg = totals[stat] / (game_count * 2)  # *2 because both teams are counted
                print(f"{stat}: {avg:.2f}")
        else:
            print("⚠️ No valid team data found.")
