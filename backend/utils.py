import os
from dotenv import load_dotenv
from typing import List
from fastapi.requests import Request as FastAPIRequest
from fastapi.templating import Jinja2Templates
from datetime import datetime
import pytz

# Load environment variables
load_dotenv()

# Paths setup
base_dir = os.path.abspath(os.path.dirname(__file__))
sixsense_root = os.path.abspath(os.path.join(base_dir, ".."))

# Initialize Jinja2 templates
templates = Jinja2Templates(directory=os.path.join(sixsense_root, "templates"))

# Flash message utilities
def flash(request: FastAPIRequest, message: str, category: str = "info"):
    messages: List = request.session.setdefault("_messages", [])
    messages.append((category, message))
    request.session["_messages"] = messages

def get_flashed_messages(request: FastAPIRequest, with_categories: bool = True) -> List:
    messages = request.session.pop("_messages", [])
    return messages if with_categories else [msg for _, msg in messages]

# Expose flash utilities to Jinja environment
templates.env.globals["get_flashed_messages"] = get_flashed_messages
templates.env.globals["flash"] = flash

# ✅ Missing function 1: Extract user_id from session
def get_user_id(request: FastAPIRequest) -> str:
    return request.session.get("user_id")

# ✅ Missing function 2: Parse match date
def parse_match_date(date_string: str) -> datetime:
    """Parses match date string and converts it to IST timezone."""
    IST = pytz.timezone("Asia/Kolkata")
    try:
        return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=pytz.utc).astimezone(IST)
    except ValueError:
        return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc).astimezone(IST)
