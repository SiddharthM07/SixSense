import os

import requests
from dotenv import load_dotenv

# to create users
# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")


def create_user(username, email, hashed_password):
    url = f"{SUPABASE_URL}/rest/v1/users"
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",  # ✅ Fix
        "Content-Type": "application/json",
    }
    data = {"username": username, "email": email, "hashed_password": hashed_password}

    response = requests.post(url, json=data, headers=headers)
    print("Response Status Code:", response.status_code)  # ✅ Debugging
    print("Response Text:", response.text)  # ✅ Debugging
    return (
        response.json()
        if response.text
        else {"message": "User created, but no JSON response"}
    )


def get_user_by_username(username):
    url = f"{SUPABASE_URL}/rest/v1/users?username=eq.{username}"
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",  # ✅ Fix
        "Content-Type": "application/json",
    }

    response = requests.get(url, headers=headers)
    print("Get User Response:", response.text)  # ✅ Debugging
    return response.json() if response.status_code == 200 else None
