import os
import requests
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta
import pytz

#To fetch all the matches from API to DB
# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# CricAPI details
API_KEY = os.getenv("CRICAPI_KEY ")
SERIES_ID = "d5a498c8-7596-4b93-8ab0-e0efc3345312"
SERIES_INFO_URL = f"https://api.cricapi.com/v1/series_info?apikey={API_KEY}&id={SERIES_ID}"

# Convert GMT time to IST by adding 5 hours and 30 minutes
def add_gmt_to_ist_offset(gmt_time_str):
    print(f"Original GMT time: {gmt_time_str}")  # Debugging step

    # Parse the input GMT time string to datetime object
    gmt_time = datetime.strptime(gmt_time_str, "%Y-%m-%dT%H:%M:%S")

    # Ensure that GMT time is timezone-aware (GMT)
    gmt_time = pytz.timezone('GMT').localize(gmt_time)

    # Convert the GMT time to IST (Indian Standard Time)
    ist_time = gmt_time.astimezone(pytz.timezone('Asia/Kolkata'))

    # Format the IST time into the desired string format
    ist_time_str = ist_time.strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"Converted IST time: {ist_time_str}")  # Debugging step
    return ist_time_str  # Return the formatted IST time as a string

def fetch_matches():
    """Fetch match list from the CricAPI series info."""
    response = requests.get(SERIES_INFO_URL)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "success" and "data" in data and "matchList" in data["data"]:
            return data["data"]["matchList"]
    print("Failed to fetch matches.")
    return []

def update_matches_table(matches):
    """Insert or update match details in Supabase."""
    for match in matches:
        match_id = match["id"]
        team1, team2 = match["teams"]
        match_date_gmt = match["dateTimeGMT"]  # Original GMT date from API

        # Convert GMT date to IST date
        match_date_ist = add_gmt_to_ist_offset(match_date_gmt)

        status = "completed" if "won" in match["status"].lower() else ("in-progress" if "progress" in match["status"].lower() else "upcoming")

        # Check if match already exists
        existing_match = supabase.table("matches").select("match_id").eq("match_id", match_id).execute()
        
        if existing_match.data:  # Update if already exists
            supabase.table("matches").update({
                "status": status,
                "match_date": match_date_ist  # Update match date to IST
            }).eq("match_id", match_id).execute()
            print(f"Updated: {team1} vs {team2} - {status}")
        else:  # Insert if new match
            supabase.table("matches").insert({
                "match_id": match_id,
                "team1": team1,
                "team2": team2,
                "match_date": match_date_ist,  # Insert match date in IST
                "status": status
            }).execute()
            print(f"Inserted: {team1} vs {team2} - {status}")

def main():
    matches = fetch_matches()
    if matches:
        update_matches_table(matches)
    else:
        print("No matches to update.")

if __name__ == "__main__":
    main()
