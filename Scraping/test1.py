import requests

API_KEY = "dee57725-c02a-4b97-9296-63a896087559"
SERIES_ID = "d5a498c8-7596-4b93-8ab0-e0efc3345312"

matches_url = f"https://api.cricapi.com/v1/series_info?apikey={API_KEY}&id={SERIES_ID}"
matches_response = requests.get(matches_url)

if matches_response.status_code == 200:
    matches_data = matches_response.json()
    print(matches_data)  # Print full response
else:
    print(f"❌ API request failed (Status Code: {matches_response.status_code})")
