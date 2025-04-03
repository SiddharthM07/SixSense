import os

import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Load Supabase API credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_API_KEY")
CRIC_API = os.getenv("CRIC_API")

API_URL = "https://api.cricapi.com/v1/series_squad?apikey=98acec87-4899-4aa7-8c9f-b12227e22465&id=d5a498c8-7596-4b93-8ab0-e0efc3345312"

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def update_players():
    response = requests.get(API_URL)

    if response.status_code == 200:
        data = response.json().get("data", [])

        # 🔹 Delete all old player data safely
        supabase.table("players").delete().neq("player_id", None).execute()

        for team in data:
            team_name = team["teamName"]
            shortname = team["shortname"]

            for player in team["players"]:
                player_data = {
                    "player_id": player["id"],
                    "name": player["name"],
                    "role": player["role"],
                    "batting_style": player.get("battingStyle", None),
                    "bowling_style": player.get("bowlingStyle", None),
                    "country": player["country"],
                    "team_name": team_name,
                    "team_shortname": shortname,
                    "player_img": player["playerImg"],
                }
                supabase.table("players").upsert(player_data).execute()

        print("✅ Players updated successfully!")
    else:
        print("❌ Failed to fetch players!")


# Run update
update_players()
