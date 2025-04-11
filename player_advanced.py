import requests
import csv

# List of player IDs
player_ids = [
    "c38b1771-9533-488c-9fca-aae42798029a",
    "a8fce43e-83c2-4e43-bcd9-3cc155d86403",
    "b7b68ab6-dd14-4682-ad70-a5074fd4d279",
    "d28866a8-e9c8-44c3-ad57-30b709796cac",
    "d39bf61e-7fef-4986-b25f-f35d9f8843a6",
    "adff7e9c-1210-4722-9657-a976e815d946",
    "c4956636-e400-4572-a3c8-811f789aac9a",
    "ddddccc5-ba64-4bb6-9351-d2a2cadbf89a",
    "bd3bcc96-5713-4441-be19-dfcb802e8ea4",
    "b685c305-c4a2-46d3-aa72-f7bc67fd0a8f",
    "fe8a6eea-d816-4fb6-ab20-3293478fe563"
]


# Cold Hearts team stats for calculations
# Team Stats based on the screenshot



team_stats = {
    "PTS": 76.0, "ORB": 15.5, "DRB": 26.1, "TRB": 41.5, "AST": 16.2,
    "TO": 17.1, "STL": 9.2, "BLK": 5.0, "PF": 18.4, "FD": 14.5,
    "2PM": 23.1, "2PA": 46.8, "2P%": 49.3, "3PM": 6.7, "3PA": 22.4,
    "3P%": 29.6, "FGM": 29.7, "FGA": 69.2, "FG%": 42.9, "FTM": 9.8,
    "FTA": 15.8, "FT%": 62.3, "+/-": -5.5
}


opponent_stats = {
    "PTS": 81.5, "ORB": 15.1, "DRB": 26.4, "TRB": 41.5, "AST": 16.5,
    "TO": 15.6, "STL": 9.7, "BLK": 4.3, "PF": 13.8, "FD": 19.1,
    "2PM": 21.1, "2PA": 40.8, "2P%": 51.6, "3PM": 8.1, "3PA": 26.8,
    "3P%": 29.9, "FGM": 29.2, "FGA": 67.5, "FG%": 43.4, "FTM": 14.3,
    "FTA": 21.1, "FT%": 67.9, "+/-": 5.5
}



# Updated Cerebro player stats based on the latest screenshot
cerebro_stats = {
    "Thomas Bassong": {"RAM": 664.6, "C-RAM": 7.3, "USG%": 22.6, "PSP": 74, "3PE": 74, "FGS": 52, "ATR": 78, "DSI": 85},
    "Logan Alexander": {"RAM": 542.7, "C-RAM": 6.0, "USG%": 15.2, "PSP": 58, "3PE": 59, "FGS": 38, "ATR": 79, "DSI": 81},
    "Jordan Skyers": {"RAM": 523.4, "C-RAM": 5.8, "USG%": 21.6, "PSP": 55, "3PE": 55, "FGS": 67, "ATR": 61, "DSI": 83},
    "Jermel Thomas": {"RAM": 508.7, "C-RAM": 5.7, "USG%": 27.1, "PSP": 80, "3PE": 80, "FGS": 76, "ATR": 48, "DSI": 71},
    "Elhadji Diallo": {"RAM": 489.6, "C-RAM": 5.5, "USG%": 18.5, "PSP": 55, "3PE": 0, "FGS": 45, "ATR": 73, "DSI": 81},
    "Yandel German": {"RAM": 391.3, "C-RAM": 4.5, "USG%": 21.4, "PSP": 50, "3PE": 50, "FGS": 68, "ATR": 51, "DSI": 79},
    "Tyriq McNeal": {"RAM": 361.2, "C-RAM": 4.2, "USG%": 13.1, "PSP": 39, "3PE": 56, "FGS": 44, "ATR": 52, "DSI": 76},
    "Kaelen Destin": {"RAM": 340.3, "C-RAM": 4.0, "USG%": 27.8, "PSP": 44, "3PE": 74, "FGS": 49, "ATR": 41, "DSI": 61},
    "Eiyilayomi Odetoyinbo": {"RAM": 321.7, "C-RAM": 3.8, "USG%": 9.4, "PSP": 32, "3PE": 0, "FGS": 31, "ATR": 48, "DSI": 69},
    "Mabilmawut Mabil": {"RAM": 299.6, "C-RAM": 3.6, "USG%": 14.9, "PSP": 35, "3PE": 51, "FGS": 28, "ATR": 53, "DSI": 59},
    "Marten Alles": {"RAM": 18.0, "C-RAM": 0.7, "USG%": 10.8, "PSP": 0, "3PE": 0, "FGS": 101, "ATR": 0, "DSI": 0}
}


# API base URL
base_url = "https://api.itsovertime.com/api/ote_players/v1/public/"
# Function to calculate advanced stats
def calculate_advanced_stats(player_stats):
    PTS = player_stats.get("points_per_game", 0)
    FGA = player_stats.get("field_goals_attempted_per_game", 0)
    FTA = player_stats.get("free_throws_attempted_per_game", 0)
    FGM = player_stats.get("field_goals_made_per_game", 0)
    FG3A = player_stats.get("three_pointers_attempted_per_game", 0)
    AST = player_stats.get("assists_per_game", 0)
    TOV = player_stats.get("turnovers_per_game", 0)
    ORB = player_stats.get("rebounds_offensive_per_game", 0)
    DRB = player_stats.get("rebounds_defensive_per_game", 0)
    STL = player_stats.get("steals_per_game", 0)
    BLK = player_stats.get("blocks_per_game", 0)
    MP = player_stats.get("minutes_per_game", 0)

    # Calculations
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

    return {
        "TSA": TSA,
        "TS%": TS_percent,
        "3PAr": threepar,
        "FTAr": ftar,
        "AST%": ast_percent,
        "TO%": to_percent,
        "ORB%": orb_percent,
        "DRB%": drb_percent,
        "STL%": stl_percent,
        "BLK%": blk_percent,
    }

# Initialize player records
player_records = []

# Process each player
for player_id in player_ids:
    response = requests.get(f"{base_url}{player_id}")
    if response.status_code != 200:
        print(f"Error fetching data for {player_id}")
        continue

    player = response.json().get("ote_player", {})
    player_name = player.get("full_name", "Unknown")

    season_stats = None
    for season in player.get("ote_seasons_ote_players", []):
        if season.get("ote_season_id") == "1b6142ab-2661-4649-af5f-d26cb5b093b4":
            season_stats = season
            break

    if not season_stats:
        print(f"No stats for {player_name}")
        continue

    adv = calculate_advanced_stats(season_stats)
    cerebro = cerebro_stats.get(player_name, {})

    player_records.append({
        "Player": player_name,
        "TSA": adv["TSA"],
        "TS%": adv["TS%"],
        "3PAr": adv["3PAr"],
        "FTAr": adv["FTAr"],
        "AST%": adv["AST%"],
        "TO%": adv["TO%"],
        "USG%": cerebro.get("USG%", "N/A"),
        "ORB%": adv["ORB%"],
        "DRB%": adv["DRB%"],
        "STL%": adv["STL%"],
        "BLK%": adv["BLK%"],
        "RAM": cerebro.get("RAM", "N/A"),
        "C-RAM": cerebro.get("C-RAM", "N/A"),
        "PSP": cerebro.get("PSP", "N/A"),
        "3PE": cerebro.get("3PE", "N/A"),
        "FGS": cerebro.get("FGS", "N/A"),
        "ATR": cerebro.get("ATR", "N/A"),
        "DSI": cerebro.get("DSI", "N/A")
    })

player_records.sort(key=lambda x: x["Player"])


# Export to CSV
csv_filename = "player_advanced_stats.csv"
fieldnames = [
    "Player", "TSA", "TS%", "3PAr", "FTAr", "AST%", "TO%", "USG%",
    "ORB%", "DRB%", "STL%", "BLK%", "RAM", "C-RAM", "PSP", "3PE", "FGS", "ATR", "DSI"
]

with open(csv_filename, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(player_records)

print(f"✅ Player advanced stats saved to {csv_filename}")