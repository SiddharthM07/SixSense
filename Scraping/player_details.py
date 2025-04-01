import os

import requests
from dotenv import load_dotenv
from supabase import Client, create_client

# TO fetch top Bastman/Bolwer from API and to insert into Table
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
CRICAPI_KEY = os.getenv("CRICAPI_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)


# Function to get match IDs where status is 'completed'
def get_completed_matches():
    response = (
        supabase.table("matches").select("match_id").eq("status", "completed").execute()
    )
    return [match["match_id"] for match in response.data]


# Function to fetch match details from CricAPI
def fetch_match_details(match_id):
    url = (
        f"https://api.cricapi.com/v1/match_scorecard?apikey={CRICAPI_KEY}&id={match_id}"
    )
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "success":
            return data.get("data", {})
    return None


# Function to extract match results
def extract_match_results(match_data):
    if not match_data:
        return "NA", "NA", "NA"

    # Get match winner
    winner = match_data.get("matchWinner", "NA")
    print(f"Match Winner: {winner}")  # Debugging output

    # Get top batsman (highest scorer)
    top_batsman = "NA"
    max_runs = 0
    for inning in match_data.get("scorecard", []):  # Iterate over innings
        for batsman in inning.get("batting", []):  # Iterate over batsmen
            runs = batsman.get("r", 0)  # Get runs scored
            if runs > max_runs:
                max_runs = runs
                top_batsman = batsman["batsman"]["name"]  # Extract batsman's name

    print(f"Top Batsman: {top_batsman} ({max_runs} runs)")  # Debugging output

    # Get top wicket-taker (most wickets)
    top_wicket_taker = "NA"
    max_wickets = 0
    for inning in match_data.get("scorecard", []):  # Iterate over innings
        for bowler in inning.get("bowling", []):  # Iterate over bowlers
            wickets = bowler.get("w", 0)  # Get wickets taken
            if wickets > max_wickets:
                max_wickets = wickets
                top_wicket_taker = bowler["bowler"]["name"]  # Extract bowler's name

    print(
        f"Top Wicket Taker: {top_wicket_taker} ({max_wickets} wickets)"
    )  # Debugging output

    return winner, top_batsman, top_wicket_taker


# Function to update match_results table
def update_match_results():
    match_ids = get_completed_matches()

    for match_id in match_ids:
        match_data = fetch_match_details(match_id)
        winner, top_batsman, top_wicket_taker = extract_match_results(match_data)

        # Insert or update match_results table
        supabase.table("match_results").upsert(
            {
                "match_id": match_id,
                "winner": winner,
                "top_batsman": top_batsman,
                "top_wicket_taker": top_wicket_taker,
            }
        ).execute()

        print(
            f"Updated results for match {match_id}: Winner - {winner}, Top Batsman - {top_batsman}, Top Wicket Taker - {top_wicket_taker}"
        )


# Run the update function
if __name__ == "__main__":
    update_match_results()
