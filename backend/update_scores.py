import os

import requests
from dotenv import load_dotenv

# not in-use
# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json",
}


def get_match_result(match_id):
    """Fetch match results for a given match."""
    url = f"{SUPABASE_URL}/rest/v1/match_results?match_id=eq.{match_id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200 and response.json():
        return response.json()[0]
    return None


def get_predictions_for_match(match_id):
    """Fetch all predictions for a specific match."""
    url = f"{SUPABASE_URL}/rest/v1/predictions?match_id=eq.{match_id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    return []


def update_user_score(user_id, points):
    """Ensure the user exists, then update or insert their score."""

    # Step 1: Check if user exists in user_scores table
    url_get = f"{SUPABASE_URL}/rest/v1/user_scores?user_id=eq.{user_id}"
    response = requests.get(url_get, headers=headers)

    if response.status_code == 200 and response.json():
        current_score = response.json()[0]["score"]
        new_score = current_score + points

        url_update = f"{SUPABASE_URL}/rest/v1/user_scores?user_id=eq.{user_id}"
        data = {"score": new_score}

        response = requests.patch(url_update, json=data, headers=headers)
        if response.status_code == 204:
            print(f"Updated score for user {user_id} to {new_score} points.")
        else:
            print(f"Failed to update score: {response.text}")

    else:
        url_insert = f"{SUPABASE_URL}/rest/v1/user_scores"
        data = {"user_id": user_id, "score": points}

        response = requests.post(url_insert, json=data, headers=headers)
        if response.status_code == 201:
            print(f"Inserted new score for user {user_id}: {points} points.")
        else:
            print(f"Failed to insert score: {response.text}")


def process_match_results(match_id):
    """Compare predictions with actual results and update scores."""
    match_result = get_match_result(match_id)

    if not match_result:
        print("No match result found.")
        return

    predictions = get_predictions_for_match(match_id)

    for prediction in predictions:
        user_id = prediction["user_id"]
        total_points = 0

        # Assign points based on correct predictions
        if prediction["winner"] == match_result["winner"]:
            total_points += 10
        if prediction["top_scorer"] == match_result["top_scorer"]:
            total_points += 5
        if prediction["top_wicket_taker"] == match_result["top_wicket_taker"]:
            total_points += 5

        if total_points > 0:
            update_user_score(user_id, total_points)



if __name__ == "__main__":
    process_match_results(1)
