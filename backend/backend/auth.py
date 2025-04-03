from database import create_user, get_user_by_username
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from pydantic import BaseModel
from starlette.status import HTTP_302_FOUND

router = APIRouter()
templates = Jinja2Templates(directory="templates")  # Ensure this path is correct

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------- [ Serve HTML Pages ] ----------------------


@router.get("/login/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register/", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# ---------------------- [ Handle Register ] ----------------------


@router.post("/signup/")
def register_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    existing_user = get_user_by_username(username)
    if existing_user and len(existing_user) > 0:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": "User already exists"}
        )

    hashed_password = pwd_context.hash(password)
    new_user = create_user(username, email, hashed_password)

    if not new_user or "error" in new_user:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": "User creation failed"}
        )

    return RedirectResponse(
        url="/auth/login/", status_code=HTTP_302_FOUND
    )  # ✅ Updated redirect


# ---------------------- [ Handle Login ] ----------------------


@router.post("/login/")
def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
    db_user = get_user_by_username(username)

    if not db_user or len(db_user) == 0:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Invalid credentials"}
        )

    db_user = db_user[0]  # Extract the first user if multiple exist

    if not pwd_context.verify(password, db_user["hashed_password"]):
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Invalid credentials"}
        )

    return RedirectResponse(
        url="/", status_code=HTTP_302_FOUND
    )  # ✅ Keeps user on home page
