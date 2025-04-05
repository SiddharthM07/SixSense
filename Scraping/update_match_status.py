import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)


import pytz

def update_match_status():
    """
    Update match statuses based on the current time:
    - Set status to "in progress" if the current time is within or past 10 minutes before the match start time.
    - Set status to "completed" if 5 hours have passed since the match start time.
    """
    # Define IST timezone
    IST = pytz.timezone("Asia/Kolkata")

    # Fetch matches that are either 'upcoming' or 'in progress'
    matches = supabase.table("matches").select("match_id, match_date, status").execute().data

    # Get current time in IST
    now = datetime.now(IST)  # Set the current time explicitly to IST

    for match in matches:
        match_id = match["match_id"]
        match_date_str = match["match_date"]

        try:
            # Parse the `match_date` with the correct format including "T"
            match_time = datetime.strptime(match_date_str, "%Y-%m-%dT%H:%M:%S")
            match_time = IST.localize(match_time)  # Ensure match_time is timezone-aware (IST)
        except ValueError as e:
            print(f"Error parsing match date {match_date_str}: {e}")
            continue  # Skip this match if there's an error

        # Debugging logs
        print(f"DEBUG: Match ID: {match_id}, Status: {match['status']}, Now (IST): {now}, Match Time (IST): {match_time}")
        print(f"DEBUG: Offset Time (10 minutes before match): {match_time - timedelta(minutes=10)}")

        # If current time is at or past 10 minutes before the match start time, update status to "in progress"
        if match["status"].strip().lower() == "upcoming" and now >= match_time - timedelta(minutes=10):
            supabase.table("matches").update({"status": "in progress"}).eq("match_id", match_id).execute()
            print(f"Match {match_id} is about to start, status updated to 'in progress'.")

        # Additional check to handle missed updates: If match is past start time and still "upcoming"
        elif match["status"].strip().lower() == "upcoming" and now >= match_time:
            supabase.table("matches").update({"status": "in progress"}).eq("match_id", match_id).execute()
            print(f"Match {match_id} started, status corrected to 'in progress'.")

        # If match started more than 5 hours ago, mark it as completed
        elif match["status"].strip().lower() == "in progress" and now >= match_time + timedelta(hours=5):
            supabase.table("matches").update({"status": "completed"}).eq("match_id", match_id).execute()
            print(f"Match {match_id} completed, status updated to 'completed'.")

if __name__ == "__main__":
    update_match_status()