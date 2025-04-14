import os
from datetime import datetime, timedelta

import pytz
from dotenv import load_dotenv
from supabase import create_client

# To update match status to completed after 5 hours
#we can schedule this as a cronjob to update the results of the matches 

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)


def update_match_status():
    # Fetch matches that are either 'upcoming' or 'in progress'
    matches = (
        supabase.table("matches").select("match_id, match_date, status").execute().data
    )

    # Define IST timezone
    IST = pytz.timezone("Asia/Kolkata")

    # Get current time in IST
    now = datetime.now(IST)  # Current IST time

    for match in matches:
        match_id = match["match_id"]
        match_date_str = match["match_date"]

        # Convert ISO format to datetime object and assume IST timezone
        match_time = datetime.strptime(match_date_str, "%Y-%m-%dT%H:%M:%S")
        match_time = IST.localize(match_time)  # Localize match time to IST

        # Debugging log to check the times
        print(f"Current IST time: {now}")
        print(f"Match time (IST): {match_time}")

        # If match has started but is not yet updated to "in progress"
        if match["status"] == "upcoming" and now >= match_time:
            supabase.table("matches").update({"status": "in progress"}).eq(
                "match_id", match_id
            ).execute()
            print(f"Match {match_id} started, status updated to 'in progress'.")

        # If match started more than 5 hours ago, mark it as completed
        elif match["status"] == "in progress" and now >= match_time + timedelta(
            hours=5
        ):
            supabase.table("matches").update({"status": "completed"}).eq(
                "match_id", match_id
            ).execute()
            print(f"Match {match_id} completed, status updated to 'completed'.")


if __name__ == "__main__":
    update_match_status()
