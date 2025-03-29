from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv
from fastapi import APIRouter
#not in-use
router = APIRouter()

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}

def get_match_status(match_id):
    """Dynamically determine match status based on match_time."""
    url = f"{SUPABASE_URL}/rest/v1/matches?match_id=eq.{match_id}&select=match_time"
    response = requests.get(url, headers=headers)

    print(f"Fetching match status for match {match_id}...")  # Debugging log
    print("Response:", response.text)

    if response.status_code == 200 and response.json():
        match_time_str = response.json()[0]["match_time"]  # Example: "2025-03-23T14:00:00Z"
        match_time = datetime.strptime(match_time_str, "%Y-%m-%dT%H:%M:%SZ")
        current_time = datetime.utcnow()

        if current_time < match_time:
            status = "upcoming"
        elif match_time <= current_time < (match_time + timedelta(hours=6)):
            status = "in-progress"
        else:
            status = "completed"

        print(f"Match {match_id} status determined as: {status}")  # Debugging log
        return status

    print(f"Match {match_id} not found.")  # Debugging log
    return None  # If no match found

def can_submit_prediction(match_id):
    """Check if predictions can be submitted."""
    match_status = get_match_status(match_id)
    print(f"Match {match_id} status: {match_status}")  # Debugging log

    return match_status == "upcoming"  # Allow only if match is upcoming

def submit_prediction(user_id, match_id, winner, top_scorer, top_wicket_taker):
    """Submit a user's prediction only if the match is upcoming."""
    if not can_submit_prediction(match_id):
        print(f" Prediction submission blocked. Match {match_id} is not upcoming.")
        return {"error": "Predictions are closed for this match."}

    url = f"{SUPABASE_URL}/rest/v1/predictions"
    data = {
        "user_id": user_id,
        "match_id": match_id,
        "winner": winner,
        "top_scorer": top_scorer,
        "top_wicket_taker": top_wicket_taker
    }

    response = requests.post(url, json=data, headers=headers)

    print(f"Submitting prediction for match {match_id}...")  # Debugging log
    print("Request Payload:", data)
    print("Response Status Code:", response.status_code)
    print("Response Text:", response.text)

    if response.status_code in [200, 201]:
        print("Prediction submitted successfully!")
        return response.json()
    else:
        print(f"Failed to submit prediction: {response.text}")
        return response.json()

# Example Usage
if __name__ == "__main__":
    match_id = 1
    user_id = 5
    winner = "RCB"
    top_scorer = "VK"
    top_wicket_taker = "KP"

    submit_prediction(user_id, match_id, winner, top_scorer, top_wicket_taker)
