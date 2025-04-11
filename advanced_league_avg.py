import requests
import csv

# Team IDs and Names
teams = {
    "Jelly Fam": "bc8b7fd0-4fd7-4559-bd03-6939cf8d158d",
    "Blue Checks": "e66d33bb-cdc2-4e29-92d6-7beb51416a0e",
    "Diamond Doves": "951ee7b6-568e-4bf7-b9f7-72390e72cbac",
    "Cold Hearts": "311c9f05-3daa-4739-8111-db97053e4971",
    "RWE": "2823e631-2735-46f7-b8f9-4250f6e9e0f5",
    "City Reapers": "6b0dab6a-71ed-4234-ac93-5a964b90cfd8",
    "YNG Dreamerz": "3ad6ec4a-dd8a-466c-8f1a-c6846ae1e7c6",
    "Fear of God Athletics": "63848a2a-fa4d-4532-bacc-d6f3866312d2"
}

# Season ID
season_id = "1b6142ab-2661-4649-af5f-d26cb5b093b4"

# CSV headers
csv_headers = ["Team", "ORTG", "DRTG", "Net RTG", "eFG%", "TO%", "ORB%", "FTAr", "POSS", "3PAr", "AST%", "PITP", "2ND CHANCE PTS", "FB PTS", "PTS OF TO", "BENCH PTS"]

# Collect stats for all teams
all_team_stats = []

for team_name, team_id in teams.items():
    print(f"Processing {team_name}...")

    response = requests.get(f"https://api.itsovertime.com/api/ote_teams/v1/public/{team_id}/ote_games?status=completed")
    if response.status_code != 200:
        print(f"Error fetching games for {team_name}: {response.status_code}")
        continue

    games_data = response.json().get("ote_games", [])

    team_stats = []

    for game in games_data:
        if game.get("ote_season_id") != season_id:
            continue

        game_teams = game.get("ote_games_ote_teams", [])
        city_team, opp_team = None, None

        for team in game_teams:
            if team["ote_team_id"] == team_id:
                city_team = team
            else:
                opp_team = team

        if city_team and opp_team:
            city_fga = city_team.get("field_goals_attempted", 0)
            city_fta = city_team.get("free_throws_attempted", 0)
            city_tov = city_team.get("turnovers", 0)
            city_orb = city_team.get("rebounds_offensive", 0)
            city_drb = city_team.get("rebounds_defensive", 0)
            city_3pa = city_team.get("points_three_attempted", 0)
            city_ast = city_team.get("assists", 0)
            city_fgm = city_team.get("field_goals_made", 0)
            opp_drb = opp_team.get("rebounds_defensive", 0)

            tsa = city_fga + 0.44 * city_fta
            possessions = 0.5 * (city_fga + 0.4 * city_fta - 1.07 * city_orb + city_tov +
                                 opp_team.get("field_goals_attempted", 0) + 0.4 * opp_team.get("free_throws_attempted", 0) -
                                 1.07 * opp_team.get("rebounds_offensive", 0) + opp_team.get("turnovers", 0))

            ortg = (city_team.get("points", 0) / possessions) * 100 if possessions else 0
            drtg = (opp_team.get("points", 0) / possessions) * 100 if possessions else 0

            stats = {
                "ORTG": ortg,
                "DRTG": drtg,
                "Net RTG": ortg - drtg,
                "eFG%": city_team.get("field_goals_effective_percentage", 0),
                "TO%": 100 * city_tov / (city_fga + 0.44 * city_fta + city_tov) if (city_fga + 0.44 * city_fta + city_tov) else 0,
                "ORB%": city_orb / (city_orb + opp_drb) * 100 if (city_orb + opp_drb) else 0,
                "FTAr": 100 * city_fta / city_fga if city_fga else 0,
                "3PAr": 100 * city_3pa / city_fga if city_fga else 0,
                "AST%": 100 * city_ast / city_fgm if city_fgm else 0,
                "POSS": possessions,
                "PITP": city_team.get("points_in_the_paint", 0),
                "2ND CHANCE PTS": city_team.get("points_second_chance", 0),
                "FB PTS": city_team.get("points_fast_break", 0),
                "PTS OF TO": city_team.get("points_from_turnover", 0),
                "BENCH PTS": city_team.get("points_from_bench", 0),
            }

            team_stats.append(stats)

    if team_stats:
        avg_stats = {k: round(sum(item[k] for item in team_stats) / len(team_stats), 2) for k in team_stats[0]}
        avg_stats["Team"] = team_name
        all_team_stats.append(avg_stats)

# Calculate league average
league_avg = {k: round(sum(team[k] for team in all_team_stats) / len(all_team_stats), 2) for k in all_team_stats[0] if k != "Team"}
league_avg["Team"] = "League Average"

# Write to CSV
with open("league_advanced_stats.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=csv_headers)
    writer.writeheader()
    for team_stat in all_team_stats:
        writer.writerow(team_stat)
    writer.writerow(league_avg)

print("✅ League-wide advanced stats saved to league_advanced_stats.csv")
