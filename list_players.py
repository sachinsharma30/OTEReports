import requests

# API Base URL
BASE_URL = "https://api.itsovertime.com"

# Dictionary of Teams with IDs
TEAMS = {
    "Jelly Fam": "bc8b7fd0-4fd7-4559-bd03-6939cf8d158d",
    "Blue Checks": "e66d33bb-cdc2-4e29-92d6-7beb51416a0e",
    "Diamond Doves": "951ee7b6-568e-4bf7-b9f7-72390e72cbac",
    "Cold Hearts": "311c9f05-3daa-4739-8111-db97053e4971",
    "RWE": "2823e631-2735-46f7-b8f9-4250f6e9e0f5",
    "City Reapers": "6b0dab6a-71ed-4234-ac93-5a964b90cfd8",
    "YNG Dreamerz": "3ad6ec4a-dd8a-466c-8f1a-c6846ae1e7c6",
    "Fear of God Athletics": "63848a2a-fa4d-4532-bacc-d6f3866312d2",
}

def fetch_team_players(team_name, team_id):
    """Fetches and displays all players from a given team ID."""
    
    # Construct the API URL
    TEAM_ENDPOINT = f"/api/ote_teams/v1/public/{team_id}"
    response = requests.get(BASE_URL + TEAM_ENDPOINT)

    if response.status_code == 200:
        data = response.json()
        team = data.get("ote_team", {})
        players = team.get("ote_players", [])

        if not players:
            print(f"\n{team_name}\nTeam ID: {team_id}\nNo players found.")
            return

        print(f"\n{team_name}\nTeam ID: {team_id}\n")
        print("PLAYER_IDS = [")
        
        player_ids = [f'    "{player["id"]}"' for player in players]
        print(",\n".join(player_ids))
        
        print("]\n")

    else:
        print(f"\nError fetching team data for {team_name}: {response.status_code}, {response.text}")

# Fetch players for all teams
for team_name, team_id in TEAMS.items():
    fetch_team_players(team_name, team_id)
