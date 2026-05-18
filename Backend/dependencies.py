import mysql.connector
from fastapi import Depends
from config import DB_NAME, DB_USERS
from auth import get_current_user


def get_guest_db():
    """Unauthenticated DB connection (register/login only)"""
    return mysql.connector.connect(
        host="localhost", user="app_guest", password=DB_USERS["guest"], database=DB_NAME
    )


def get_db_for_role(role: str):
    db_user = "app_student" if role == "student" else "app_admin"
    password = DB_USERS["student"] if role == "student" else DB_USERS["admin"]

    return mysql.connector.connect(
        host="localhost", user=db_user, password=password, database=DB_NAME
    )


async def get_authenticated_db(current_user: dict = Depends(get_current_user)):
    db = get_db_for_role(current_user["role"])
    try:
        yield db
    finally:
        db.close()
