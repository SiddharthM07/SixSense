import os
import subprocess
import time

import uvicorn
from database import create_user, get_user_by_username
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_302_FOUND
from supabase import create_client

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Initialize FastAPI app
app = FastAPI()

# Add Session Middleware
app.add_middleware(SessionMiddleware, secret_key="your_secret_key_here")

# Initialize FastAPI router
router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define paths at the beginning
sixsense_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
frontend_dir = os.path.join(sixsense_root, "Frontend")
frontend_path = os.path.join(frontend_dir, "routes.py")

# ---------------------- [ Serve HTML Pages ] ----------------------


@router.get("/login/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register/", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# ---------------------- [ Handle Register ] ----------------------


@router.post("/signup/")
def register_user(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    existing_user = get_user_by_username(username)
    if existing_user and len(existing_user) > 0:
        return templates.TemplateResponse("register.html", {"request": request, "error": "User already exists"})

    hashed_password = pwd_context.hash(password)
    new_user = create_user(username, email, hashed_password)

    if not new_user or "error" in new_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "User creation failed"})

    return RedirectResponse(url="/login/", status_code=HTTP_302_FOUND)


# ---------------------- [ Handle Login ] ----------------------


@router.post("/login/")
def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
    db_user = get_user_by_username(username)

    if not db_user or len(db_user) == 0:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

    db_user = db_user[0]

    if not pwd_context.verify(password, db_user["hashed_password"]):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

    request.session["user_id"] = db_user["id"]

    return RedirectResponse(url=f"http://127.0.0.1:5000/matches?user_id={db_user['id']}", status_code=303)


# Include router in the FastAPI app
app.include_router(router)

# ---------------------- [ Leaderboard API ] ----------------------


@router.get("/leaderboard", response_class=JSONResponse)
def get_leaderboard(request: Request):
    try:
        response = (
            supabase.table("user_scores")
            .select("user_id, score, users(username)")
            .execute()
        )

        if not response.data:
            return JSONResponse(content={"error": "No leaderboard data found"}, status_code=404)

        user_scores = {}
        for row in response.data:
            if "users" in row and row["users"]:
                username = row["users"]["username"]
                score = row["score"]
                user_scores[username] = user_scores.get(username, 0) + score

        sorted_leaderboard = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
        leaderboard = []
        prev_score = None
        current_rank = 0
        skip_count = 0

        for idx, (user, score) in enumerate(sorted_leaderboard):
            if score == prev_score:
                rank = current_rank
                skip_count += 1
            else:
                rank = idx + 1 - skip_count
                current_rank = rank
                prev_score = score

            leaderboard.append({"rank": rank, "username": user, "total_score": score})

        return templates.TemplateResponse("leaderboard.html", {"request": request, "leaderboard": leaderboard})

    except Exception as e:
        print("Error fetching leaderboard:", str(e))
        return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)


# ---------------------- [ LOGOUT ] ----------------------


@router.get("/logout/")
def logout(request: Request):
    request.session.clear()
    print("User logged out")
    return RedirectResponse(url="/login/", status_code=303)


app.include_router(router)

# ---------------------- [ Start Flask Automatically ] ----------------------

if not os.path.exists(frontend_path):
    raise FileNotFoundError(f"Error: routes.py not found at {frontend_path}")

flask_process = subprocess.Popen(
    ["python3", frontend_path],
    cwd=frontend_dir,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

time.sleep(3)

if __name__ == "__main__":
    try:
        uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        if 'flask_process' in locals():
            flask_process.terminate()
