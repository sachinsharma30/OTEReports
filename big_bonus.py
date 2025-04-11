import requests
import csv

# Specify the team you want to see (example: "City Reapers")
SPECIFIED_TEAM = "Fear of God Athletics"

# API Endpoints
API_URLS = {
    "bb.csv": "https://api.itsovertime.com/api/ote_stats/v1/public/big_bonus/offensive",
    "opp_bb.csv": "https://api.itsovertime.com/api/ote_stats/v1/public/big_bonus/defensive"
}

# Season ID
ote_season_id = "1b6142ab-2661-4649-af5f-d26cb5b093b4"

# Functions
def calculate_fg_percentage(made, attempted):
    return round((float(made) / float(attempted) * 100), 2) if float(attempted) > 0 else "-"

def calculate_pps(fgm, fga, multiplier):
    return round((multiplier * float(fgm) / float(fga)), 2) if float(fga) > 0 else 0

def rank_custom(values_dict):
    sorted_items = sorted(values_dict.items(), key=lambda x: x[1], reverse=True)
    return {team: rank + 1 for rank, (team, _) in enumerate(sorted_items)}

def process_data(api_url, output_filename):
    response = requests.get(f"{api_url}?ote_season_ids={ote_season_id}")
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        return

    data = response.json()["big_bonus_teams"]

    # Prepare ranking data
    pps_two, pps_three, pps_all = {}, {}, {}
    two_fga, three_fga, all_fga = {}, {}, {}
    foul_fga = {team["ote_team_name"]: int(float(team["FD"])) for team in data if float(team["FD"]) > 0}

    for team in data:
        team_name = team["ote_team_name"]

        # Shot data
        two_fgm, two_fga_val = int(float(team["2PM"])), int(float(team["2PA"]))
        three_fgm, three_fga_val = int(float(team["3PM"])), int(float(team["3PA"]))
        total_fgm = two_fgm + three_fgm
        total_fga_val = two_fga_val + three_fga_val

        # PPS calculations
        if two_fga_val > 0:
            pps_two[team_name] = calculate_pps(two_fgm, two_fga_val, 2)
            two_fga[team_name] = two_fga_val

        if three_fga_val > 0:
            pps_three[team_name] = calculate_pps(three_fgm, three_fga_val, 3)
            three_fga[team_name] = three_fga_val

        if total_fga_val > 0:
            pps_all[team_name] = calculate_pps(total_fgm, total_fga_val, 2.5)
            all_fga[team_name] = total_fga_val

    # Compute ranks
    two_fga_rank = rank_custom(two_fga)
    two_pps_rank = rank_custom(pps_two)

    three_fga_rank = rank_custom(three_fga)
    three_pps_rank = rank_custom(pps_three)

    foul_fga_rank = rank_custom(foul_fga)
    foul_pps_rank = {team: 1 for team in foul_fga}  # Fouls PPS is constant

    all_shots_fga_rank = rank_custom(all_fga)
    all_shots_pps_rank = rank_custom(pps_all)

    # CSV Output (without team name column)
    headers = ["Shot Types", "FGM", "FGA", "FG%", "PPS", "FGA RANK", "PPS RANK"]

    with open(output_filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)

        # Find specified team data
        team_data = next((team for team in data if team["ote_team_name"] == SPECIFIED_TEAM), None)

        if not team_data:
            print(f"⚠️ Specified team '{SPECIFIED_TEAM}' not found in data.")
            return

        team_name = team_data["ote_team_name"]

        # Shot Data
        two_fgm, two_fga_val = int(float(team_data["2PM"])), int(float(team_data["2PA"]))
        three_fgm, three_fga_val = int(float(team_data["3PM"])), int(float(team_data["3PA"]))
        total_fgm = two_fgm + three_fgm
        total_fga_val = two_fga_val + three_fga_val
        fouls_drawn = int(float(team_data["FD"]))

        # FG% Calculations
        two_fg_percent = calculate_fg_percentage(two_fgm, two_fga_val)
        three_fg_percent = calculate_fg_percentage(three_fgm, three_fga_val)
        total_fg_percent = calculate_fg_percentage(total_fgm, total_fga_val)

        # PPS
        two_pps = pps_two.get(team_name, 0)
        three_pps = pps_three.get(team_name, 0)
        total_pps = pps_all.get(team_name, 0)

        # Write rows without team name
        writer.writerow(["Two Pointers", two_fgm, two_fga_val, two_fg_percent, two_pps,
                         two_fga_rank.get(team_name, "-"), two_pps_rank.get(team_name, "-")])

        writer.writerow(["Three Pointers", three_fgm, three_fga_val, three_fg_percent, three_pps,
                         three_fga_rank.get(team_name, "-"), three_pps_rank.get(team_name, "-")])

        writer.writerow(["Fouls", "-", fouls_drawn, "-", 2.0,
                         foul_fga_rank.get(team_name, "-"), foul_pps_rank.get(team_name, "-")])

        writer.writerow(["All Shots", total_fgm, total_fga_val, total_fg_percent, total_pps,
                         all_shots_fga_rank.get(team_name, "-"), all_shots_pps_rank.get(team_name, "-")])

    print(f"✅ {SPECIFIED_TEAM} Big Bonus Breakdown saved to {output_filename}")

# Process both offensive and defensive
process_data(API_URLS["bb.csv"], "bb.csv")
process_data(API_URLS["opp_bb.csv"], "opp_bb.csv")
