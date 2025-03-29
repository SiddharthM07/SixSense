import os
import requests
from dotenv import load_dotenv
#Handles database queries for matches and predictions
# Load environment variables
load_dotenv()
#not in-use

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}

def get_match_by_id(match_id):
    """Fetch match details by match_id from the database."""
    url = f"{SUPABASE_URL}/rest/v1/matches?match_id=eq.{match_id}"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200 and response.text.strip():
        match_data = response.json()
        return match_data[0] if match_data else None  # Ensure we return the first match object
    return None

def get_prediction_by_user_and_match(user_id, match_id):
    """Check if a user has already made a prediction for a specific match."""
    url = f"{SUPABASE_URL}/rest/v1/predictions?user_id=eq.{user_id}&match_id=eq.{match_id}"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200 and response.text.strip():
        return response.json()
    return None

def save_prediction(user_id, match_id, winner, top_scorer, top_wicket_taker):
    """Save a new prediction into the Supabase database."""
    url = f"{SUPABASE_URL}/rest/v1/predictions"
    data = {
        "user_id": user_id,
        "match_id": match_id,
        "winner": winner,
        "top_scorer": top_scorer,
        "top_wicket_taker": top_wicket_taker
    }

    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code in [200, 201]:  # Success codes for insertion
        return {"message": "Prediction saved successfully"}
    
    return {"error": "Failed to save prediction"}
