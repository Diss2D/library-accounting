import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

DATABASE_URL = os.environ["DATABASE_URL"]
JWT_SECRET = os.environ["JWT_SECRET"]
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

if len(JWT_SECRET) < 32 or JWT_SECRET == "CHANGE_ME":
    raise ValueError("Укажите JWT_SECRET длиной не менее 32 символов")
