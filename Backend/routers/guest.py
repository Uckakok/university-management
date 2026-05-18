from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import socket
import mysql.connector
from models import UserRegister
from dependencies import get_guest_db
from auth import create_access_token

router = APIRouter(tags=["public"])


@router.post("/register")
async def register(user: UserRegister, db=Depends(get_guest_db)):
    cursor = db.cursor()
    try:
        cursor.callproc(
            "register_user",
            [
                user.name,
                user.second_name,
                user.surname,
                user.gender.value,
                user.login,
                user.password,
            ],
        )
        db.commit()
        return {"status": "success", "message": f"User {user.login} created"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()


@router.post("/login")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db=Depends(get_guest_db),
):
    cursor = db.cursor()
    try:
        client_ip = request.client.host
        binary_ip = socket.inet_aton(client_ip) if client_ip else b"\x00\x00\x00\x00"

        args = (form_data.username, form_data.password, binary_ip, "", 0, False)
        result_args = cursor.callproc("login_user", args)

        role, person_id, success = result_args[3], result_args[4], result_args[5]

        if not success:
            raise HTTPException(status_code=401, detail="Invalid login or password")

        db.commit()
        access_token = create_access_token(
            data={"sub": form_data.username, "role": role, "pid": person_id}
        )
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        cursor.close()
