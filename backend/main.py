import os
import sys
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_302_FOUND
from passlib.context import CryptContext
from supabase import create_client
from fastapi.templating import Jinja2Templates

# ---------------------- [ Paths Setup ] ----------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
base_dir = os.path.abspath(os.path.dirname(__file__))
sixsense_root = os.path.abspath(os.path.join(base_dir, ".."))

# ---------------------- [ ENV + Supabase Init ] ----------------------
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# ---------------------- [ FastAPI App Init ] ----------------------
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("FLASK_SECRET_KEY", "your_secret_key_here"))

# ✅ Initialize templates here
templates = Jinja2Templates(directory=os.path.join(sixsense_root, "templates"))

# ---------------------- [ Import Utility Functions ] ----------------------
from utils import flash, get_flashed_messages

# ✅ Updated wrapper function to include `request` explicitly
def get_flashed_messages_wrapper(request, *args, **kwargs):
    # Pass `request` and additional arguments to the original function
    return get_flashed_messages(request, *args, **kwargs)

# ✅ Register globals for Jinja2 templates
templates.env.globals["get_flashed_messages"] = get_flashed_messages_wrapper
templates.env.globals["flash"] = flash

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------- [ Auth Routes ] ----------------------
auth_router = APIRouter()
from database import create_user, get_user_by_username

@auth_router.get("/login/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@auth_router.get("/register/", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@auth_router.post("/signup/")
def register_user(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    if get_user_by_username(username):
        return templates.TemplateResponse("register.html", {"request": request, "error": "User already exists"})
    
    hashed_password = pwd_context.hash(password)
    new_user = create_user(username, email, hashed_password)
    
    if not new_user or "error" in new_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "User creation failed"})

    return RedirectResponse(url="/login/", status_code=HTTP_302_FOUND)

@auth_router.post("/login/")
def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
    db_user = get_user_by_username(username)
    if not db_user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

    db_user = db_user[0]
    if not pwd_context.verify(password, db_user["hashed_password"]):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

    request.session["user_id"] = db_user["id"]
    return RedirectResponse(url=f"/matches?user_id={db_user['id']}", status_code=303)

@auth_router.get("/logout/")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login/", status_code=303)

app.include_router(auth_router)

# ---------------------- [ Leaderboard API ] ----------------------
@auth_router.get("/leaderboard", response_class=JSONResponse, name="leaderboard")
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

app.include_router(auth_router)

# ---------------------- [ Import Frontend Routes ] ----------------------
from Frontend.routes import router as frontend_router
app.include_router(frontend_router)

# ---------------------- [ Run FastAPI ] ----------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)