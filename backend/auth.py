from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from database import create_user, get_user_by_username

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

@app.post("/signup/")
def signup(user: UserCreate):
    # Check if user already exists
    existing_user = get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Hash password and store in Supabase
    hashed_password = pwd_context.hash(user.password)
    new_user = create_user(user.username, user.email, hashed_password)

    if "error" in new_user:
        raise HTTPException(status_code=500, detail="User creation failed")

    return {"message": "User registered successfully"}

@app.post("/login/")
def login(user: UserLogin):
    db_user = get_user_by_username(user.username)

    # Check if user exists
    if not db_user or len(db_user) == 0:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    db_user = db_user[0]  # Get the first dictionary from the list

    # Verify password
    if not pwd_context.verify(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Login successful"}
