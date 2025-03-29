from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from supabase import create_client
import os
import requests
from datetime import datetime,timedelta
from dotenv import load_dotenv
import pytz


# Define IST timezone
ist = pytz.timezone('Asia/Kolkata')

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your_secret_key")  # Ensure session security

# Supabase client setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Define team colors
TEAM_COLORS = {
    "Chennai Super Kings": "#FECB00",
    "Mumbai Indians": "#045093",
    "Royal Challengers Bengaluru": "#DA1818",
    "Kolkata Knight Riders": "#3A225D",
    "Sunrisers Hyderabad": "#FA761E",
    "Rajasthan Royals": "#EA1A7C",
    "Delhi Capitals": "#17449B",
    "Punjab Kings": "#D71920",
    "Lucknow Super Giants": "#004C93",
    "Gujarat Titans": "#1C2C3B"
}

@app.route('/')
@app.route('/matches')
def get_matches():
    """ Fetch and display all matches from Supabase """
    
    # ✅ Get user_id from query parameters (if coming from FastAPI)
    user_id = request.args.get("user_id")
    if user_id:
        session["user_id"] = user_id  # Store in Flask session

    if not SUPABASE_URL or not SUPABASE_API_KEY:
        return jsonify({"error": "Supabase credentials are missing"}), 500

    headers = {"apikey": SUPABASE_API_KEY}
    try:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/matches", headers=headers)
        response.raise_for_status()
        matches = response.json()
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch matches: {e}"}), 500

    now = datetime.now()  # Local system time in IST

    for match in matches:
        try:
            match_time_str = match['match_date'].replace('T', ' ')
            match_time = datetime.strptime(match_time_str, "%Y-%m-%d %H:%M:%S")
            time_diff = (match_time - now).total_seconds()

            prediction_open = (time_diff >= 10 * 60) and (time_diff <= 30 * 3600)
            match['prediction_open'] = prediction_open
            match['match_date_display'] = match['match_date'].replace('T', ' ')

        except ValueError as e:
            print(f"Error parsing date for match {match}: {e}")

    matches.sort(key=lambda x: x['match_date'])

    return render_template("matches.html", matches=matches, team_colors=TEAM_COLORS)


@app.route('/predict/<match_id>')
def predict(match_id):
    """ Show the prediction page for a selected match """

    # ✅ Ensure user is logged in
    if "user_id" not in session:
        return redirect(url_for("login"))

    match_response = supabase.table("matches").select("*").eq("match_id", match_id).execute()
    match = match_response.data[0] if match_response.data else None

    if not match:
        return "Match not found!", 404

    team1, team2 = match["team1"], match["team2"]
    players_response = supabase.table("players").select("*").execute()
    all_players = players_response.data if players_response.data else []

    team1_players = [p for p in all_players if p["team_name"] == team1]
    team2_players = [p for p in all_players if p["team_name"] == team2]

    batsmen = [p for p in team1_players + team2_players if "Batsman" in p["role"] or "WK-Batsman" in p["role"] or "Batting Allrounder" in p["role"]]
    bowlers = [p for p in team1_players + team2_players if "Bowler" in p["role"] or "Bowling Allrounder" in p["role"]]

    return render_template("predict.html", match=match, batsmen=batsmen, bowlers=bowlers)


@app.route('/submit_prediction', methods=['POST'])
def submit_prediction():
    try:
        user_id = request.form.get('user_id')
        match_id = request.form.get('match_id')
        top_scorer = request.form.get('top_scorer')
        top_wicket_taker = request.form.get('top_wicket_taker')
        winner = request.form.get('winner')

        print("📌 User ID:", user_id)
        print("📌 Match ID:", match_id)
        print("📌 Top Scorer:", top_scorer)
        print("📌 Top Wicket Taker:", top_wicket_taker)
        print("📌 Winner:", winner)

        if not user_id or not match_id or not top_scorer or not top_wicket_taker or not winner:
            flash("All fields are required!", "error")
            return redirect(url_for('get_matches'))

        # Fetch match date from database
        match_response = supabase.table("matches").select("match_date") \
            .eq("match_id", match_id).execute()

        if not match_response.data:
            flash("Match not found!", "error")
            return redirect(url_for('get_matches'))

        # ✅ Fix: Parse 'YYYY-MM-DDTHH:MM:SS' correctly
        match_time_str = match_response.data[0]["match_date"]  # Extract string
        match_time_ist = datetime.strptime(match_time_str, "%Y-%m-%dT%H:%M:%S")  # Parse correctly
        match_time_ist = ist.localize(match_time_ist)  # Assign IST timezone
        match_time_utc = match_time_ist.astimezone(pytz.UTC)  # Convert to UTC

        # Get current UTC time
        current_time_utc = datetime.utcnow().replace(tzinfo=pytz.UTC)

        # Check if predictions are locked (10 minutes before match start)
        if match_time_utc - current_time_utc < timedelta(minutes=10):  # ✅ Now timedelta works
            flash("Predictions are locked 10 minutes before match start!", "error")
            return redirect(url_for('get_matches'))

        # Check if prediction already exists
        existing_response = supabase.table("predictions").select("*") \
            .eq("user_id", user_id).eq("match_id", match_id).execute()

        print("🔍 Existing Prediction Response:", existing_response)

        if existing_response.data and len(existing_response.data) > 0:
            # Update the existing prediction instead of blocking it
            update_response = supabase.table("predictions").update({
                "top_scorer": top_scorer,
                "top_wicket_taker": top_wicket_taker,
                "winner": winner
            }).eq("user_id", user_id).eq("match_id", match_id).execute()

            print("🔄 Update Response:", update_response)
            flash("Prediction updated successfully!", "success")
        else:
            # Insert a new prediction
            insert_response = supabase.table("predictions").insert({
                "user_id": user_id,
                "match_id": match_id,
                "top_scorer": top_scorer,
                "top_wicket_taker": top_wicket_taker,
                "winner": winner
            }).execute()

            print("📌 Insert Response:", insert_response)
            flash("Prediction submitted successfully!", "success")

        return redirect(url_for('get_matches'))

    except Exception as e:
        print("🔥 Exception:", e)  # Debugging
        flash(f"Unexpected error: {str(e)}", "error")
        return redirect(url_for('get_matches'))

@app.route('/view_results/<match_id>')
def view_results(match_id):
    """ Display match results, user's prediction, and their score """

    user_id = session.get("user_id")  # Get logged-in user ID from session
    if not user_id:
        flash("You must be logged in to view results.", "error")
        return redirect(url_for("login"))

    # Fetch match details
    match_response = supabase.table("matches").select("*").eq("match_id", match_id).execute()
    match = match_response.data[0] if match_response.data else None

    if not match:
        flash("Match not found!", "error")
        return redirect(url_for("get_matches"))

    # Fetch actual match results
    results_response = supabase.table("match_results").select("*").eq("match_id", match_id).execute()
    results = results_response.data[0] if results_response.data else None

    # Fetch the logged-in user's prediction
    user_prediction_response = (
        supabase.table("predictions")
        .select("*")
        .eq("match_id", match_id)
        .eq("user_id", user_id)
        .execute()
    )
    user_prediction = user_prediction_response.data[0] if user_prediction_response.data else None

    # Fetch user's score for this match (only if they made a prediction)
    if user_prediction:
        match_score_response = (
            supabase.table("user_scores")
            .select("score")
            .eq("user_id", user_id)
            .eq("match_id", match_id)
            .execute()
        )
        match_score = match_score_response.data[0]["score"] if match_score_response.data else 0
    else:
        match_score = None  # No score if no prediction

    # Fetch user's total score across all matches
    total_score_response = (
        supabase.table("user_scores")
        .select("score")
        .eq("user_id", user_id)
        .execute()
    )
    total_score = sum(entry["score"] for entry in total_score_response.data) if total_score_response.data else 0

    return render_template(
        'view_results.html',
        match=match,
        results=results,
        user_prediction=user_prediction,  # This can now be None
        match_score=match_score,
        total_score=total_score
    )



if __name__ == '__main__':
    app.run(debug=True)
