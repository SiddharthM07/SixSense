import os
import sys
from datetime import datetime, timedelta

import pytz
import requests
from dotenv import load_dotenv
from fastapi import APIRouter, Form, HTTPException, Query, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from supabase import create_client

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from utils import get_user_id, parse_match_date, flash  # Importing utility functions

# ✅ Lazy import function to avoid circular import
def get_templates():
    from main import templates
    return templates

# Constants and setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)
router = APIRouter()

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
    "Gujarat Titans": "#1C2C3B",
}
IST = pytz.timezone("Asia/Kolkata")


@router.get("/", response_class=HTMLResponse)
@router.get("/matches", response_class=HTMLResponse)
async def get_matches(request: Request, user_id: str = Query(default=None)):
    templates = get_templates()  # ✅ Use lazy import here

    if user_id:
        request.session["user_id"] = user_id

    try:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/matches", headers={"apikey": SUPABASE_API_KEY})
        response.raise_for_status()
        matches = response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch matches: {e}")

    now = datetime.now(IST)
    for match in matches:
        try:
            match_time = parse_match_date(match["match_date"])
            match["prediction_open"] = 600 <= (match_time - now).total_seconds() <= 108000
            match["match_date_display"] = match["match_date"].replace("T", " ")
        except Exception as e:
            print(f"⚠️ Error parsing match date: {e}")

    matches.sort(key=lambda x: x["match_date"])
    return templates.TemplateResponse(
        "matches.html",
        {"request": request, "matches": matches, "team_colors": TEAM_COLORS},
    )


@router.get("/predict/{match_id}", response_class=HTMLResponse)
async def predict(request: Request, match_id: str):
    """Show the prediction page for a selected match"""

    templates = get_templates()

    # Ensure user is logged in
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login")

    # Fetch match details
    match_response = supabase.table("matches").select("*").eq("match_id", match_id).execute()
    match = match_response.data[0] if match_response.data else None
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # Fetch all players
    players_response = supabase.table("players").select("*").execute()
    all_players = players_response.data if players_response.data else []

    # Filter players by team
    team1_players = [p for p in all_players if p["team_name"] == match["team1"]]
    team2_players = [p for p in all_players if p["team_name"] == match["team2"]]

    # Classify players by role
    batsmen = [
        p
        for p in team1_players + team2_players
        if "Batsman" in p["role"] or "WK-Batsman" in p["role"] or "Batting Allrounder" in p["role"]
    ]
    bowlers = [
        p
        for p in team1_players + team2_players
        if "Bowler" in p["role"] or "Bowling Allrounder" in p["role"]
    ]

    # Pass session explicitly to the template context
    return templates.TemplateResponse(
        "predict.html",
        {
            "request": request,
            "session": request.session,  # ✅ Include session in the context
            "match": match,
            "batsmen": batsmen,
            "bowlers": bowlers,
        },
    )

@router.post("/submit_prediction")
async def submit_prediction(
    request: Request,
    match_id: str = Form(...),
    top_scorer: str = Form(...),
    top_wicket_taker: str = Form(...),
    winner: str = Form(...),
):
    """Submit or update a user's match prediction"""

    user_id = request.session.get("user_id")
    if not user_id:
        flash(request, "You must be logged in to submit predictions!", "error")
        return RedirectResponse("/matches", status_code=302)

    # Fetch match date
    match_res = supabase.table("matches").select("match_date").eq("match_id", match_id).execute()
    match_data = match_res.data[0] if match_res.data else None
    if not match_data:
        flash(request, "Match not found!", "error")
        return RedirectResponse("/matches", status_code=302)

    # Parse match time as offset-aware
    match_time = parse_match_date(match_data["match_date"])  # Assuming this function makes the datetime offset-aware

    # Convert `datetime.utcnow()` to offset-aware
    from datetime import datetime, timezone
    now = datetime.utcnow().replace(tzinfo=timezone.utc)  # Convert naive to UTC offset-aware

    # Ensure predictions are submitted within the allowed time range
    if now + timedelta(minutes=10) > match_time:
        flash(request, "Predictions are locked 10 minutes before match start!", "error")
        return RedirectResponse("/matches", status_code=302)

    # Check for existing predictions
    existing_pred = supabase.table("predictions").select("*").eq("user_id", user_id).eq("match_id", match_id).execute()
    if existing_pred.data:
        supabase.table("predictions").update(
            {"top_scorer": top_scorer, "top_wicket_taker": top_wicket_taker, "winner": winner}
        ).eq("user_id", user_id).eq("match_id", match_id).execute()
        flash(request, "Prediction updated successfully!", "success")
    else:
        supabase.table("predictions").insert(
            {"user_id": user_id, "match_id": match_id, "top_scorer": top_scorer, "top_wicket_taker": top_wicket_taker, "winner": winner}
        ).execute()
        flash(request, "Prediction submitted successfully!", "success")

    return RedirectResponse("/matches", status_code=302)


@router.get("/view_results/{match_id}", response_class=HTMLResponse)
async def view_results(request: Request, match_id: str):
    """Display match results, user's prediction, and their score"""

    templates = get_templates()
    user_id = get_user_id(request)
    if not user_id:
        flash(request, "You must be logged in to view results.", "error")
        return RedirectResponse("/login")

    match_res = supabase.table("matches").select("*").eq("match_id", match_id).execute()
    match = match_res.data[0] if match_res.data else None
    if not match:
        flash(request, "Match not found!", "error")
        return RedirectResponse("/matches", status_code=302)

    results_res = supabase.table("match_results").select("*").eq("match_id", match_id).execute()
    results = results_res.data[0] if results_res.data else None

    pred_res = supabase.table("predictions").select("*").eq("match_id", match_id).eq("user_id", user_id).execute()
    user_prediction = pred_res.data[0] if pred_res.data else None

    match_score_res = supabase.table("user_scores").select("score").eq("user_id", user_id).eq("match_id", match_id).execute()
    match_score = match_score_res.data[0]["score"] if match_score_res.data else 0

    total_score_res = supabase.table("user_scores").select("score").eq("user_id", user_id).execute()
    total_score = sum(entry["score"] for entry in total_score_res.data) if total_score_res.data else 0

    return templates.TemplateResponse(
        "view_results.html",
        {
            "request": request,
            "match": match,
            "results": results,
            "user_prediction": user_prediction,
            "match_score": match_score,
            "total_score": total_score,
        },
    )