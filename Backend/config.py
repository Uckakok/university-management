import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

SECRET_KEY = os.getenv("APP_SECRET_KEY", "dev-secret-do-not-use-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

DB_NAME = os.getenv("DATABASE_NAME", "university")

DB_USERS = {
    "guest": os.getenv("DB_GUEST_PASSWORD", "temp_guest_pass"),
    "student": os.getenv("DB_STUDENT_PASSWORD", "temp_student_pass"),
    "admin": os.getenv("DB_ADMIN_PASSWORD", "temp_admin_pass"),
}
