from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr, BeforeValidator
import mysql.connector
import os
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional, Annotated
from fastapi.security import OAuth2PasswordRequestForm
import socket
from fastapi import Request
from typing import List
from functools import wraps

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
app = FastAPI()
SECRET_KEY = os.getenv("APP_SECRET_KEY", "dev-secret-do-not-use-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class GenderEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"
    PREFER_NOT_TO_SAY = "Prefer not to say"


@app.get("/metadata/genders")
async def get_genders():
    return [g.value for g in GenderEnum]

def get_allowed_origins() -> List[str]:
    origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5500")
    return [origin.strip() for origin in origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {
            "user_id": user_id,
            "role": payload.get("role"),
            "pid": payload.get("pid"),
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


def empty_to_none(v: str | None) -> str | None:
    if v == "" or (isinstance(v, str) and not v.strip()):
        return None
    return v


class UserRegister(BaseModel):
    name: str = Field(..., min_length=3, max_length=64)
    second_name: Annotated[Optional[str], BeforeValidator(empty_to_none)] = Field(
        None, min_length=3, max_length=64
    )
    surname: str = Field(..., min_length=3, max_length=64)
    gender: GenderEnum
    login: str = Field(..., min_length=3, max_length=32)
    password: str


def require_roles(allowed_roles: List[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(
            current_user: dict = Depends(get_current_user), *args, **kwargs
        ):
            if current_user["role"] not in allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Access denied. Required roles: {allowed_roles}",
                )
            return await func(current_user=current_user, *args, **kwargs)

        return wrapper

    return decorator


def get_guest_db():
    db_name = os.getenv("DATABASE_NAME", "university")
    guest_password = os.getenv('DB_GUEST_PASSWORD', 'temp_guest_pass')
    
    return mysql.connector.connect(
        host="localhost",
        user='app_guest',
        password=guest_password,
        database=db_name
    )

async def get_authenticated_db(current_user: dict = Depends(get_current_user)):
    db = get_db_connection_for_role(current_user['role'])
    try:
        yield db
    finally:
        db.close()

def get_db_connection_for_role(role: str):
    db_name = os.getenv("DATABASE_NAME", "university")
    if role == 'administrator':
        user = 'app_admin'
        password = os.getenv('DB_ADMIN_PASSWORD', 'temp_admin_pass')
    else:
        user = 'app_student'
        password = os.getenv('DB_STUDENT_PASSWORD', 'temp_student_pass')
    
    return mysql.connector.connect(
        host="localhost",
        user=user,
        password=password,
        database=db_name
    )

@app.post("/register")
async def register(user: UserRegister, db = Depends(get_guest_db)):
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
        db.close()


@app.post("/login")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db = Depends(get_guest_db),
):
    cursor = db.cursor()

    try:
        client_ip = request.client.host

        try:
            binary_ip = socket.inet_aton(client_ip)
        except socket.error:
            binary_ip = b"\x00\x00\x00\x00"

        args = (form_data.username, form_data.password, binary_ip, "", 0, False)

        result_args = cursor.callproc("login_user", args)

        role = result_args[3]
        person_id = result_args[4]
        success = result_args[5]

        if not success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login or password",
            )

        db.commit()

        access_token = create_access_token(
            data={"sub": form_data.username, "role": role, "pid": person_id}
        )

        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        db.close()


class CandidateRegister(BaseModel):
    nationality: str = Field(..., min_length=2, max_length=2, pattern=r"^[A-Z]{2}$")
    pesel: str = Field(..., min_length=11, max_length=11, pattern=r"^\d{11}$")
    email_address: EmailStr
    phone_number: str = Field(..., pattern=r"^\+?[\d\s\-]{7,15}$")
    address: str = Field(..., min_length=5, max_length=255)


@app.post("/register_candidate")
async def register_candidate(
    Data: CandidateRegister,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_authenticated_db),
):
    cursor = db.cursor()
    try:
        cursor.callproc(
            "register_candidate",
            [
                current_user["pid"],
                Data.nationality,
                Data.pesel,
                Data.email_address,
                Data.phone_number,
                Data.address,
            ],
        )
        db.commit()
        return {"status": "success", "message": "Registered candidate"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()
        db.close()


class ApplicationReject(BaseModel):
    id_application: int


@app.get("/get_applications")
@require_roles(["administrator"])
async def get_applications(
    current_user: dict = Depends(get_current_user), db = Depends(get_authenticated_db)
):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.callproc("get_applications")

        applications = []
        for result in cursor.stored_results():
            applications = result.fetchall()

        return {"applications": applications}
    finally:
        cursor.close()
        db.close()


@app.post("/reject_application")
@require_roles(["administrator"])
async def reject_application(
    Data: ApplicationReject,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_authenticated_db),
):
    cursor = db.cursor()
    employee_id = get_employee_id_from_people_id(current_user["pid"], db)
    try:
        cursor.callproc("reject_application", [Data.id_application, employee_id])
        db.commit()
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()
        db.close()


class ApplicationApprove(BaseModel):
    id_application: int


@app.post("/approve_application")
@require_roles(["administrator"])
async def approve_application(
    Data: ApplicationApprove,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_authenticated_db),
):
    cursor = db.cursor()
    employee_id = get_employee_id_from_people_id(current_user["pid"], db)
    try:
        cursor.callproc("approve_application", [Data.id_application, employee_id])
        db.commit()
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()
        db.close()


class ProcessSemesterTransition(BaseModel):
    id_student: int


@app.post("/process_semester_transition")
@require_roles(["administrator"])
async def process_semester_transition(
    Data: ProcessSemesterTransition,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_authenticated_db),
):
    cursor = db.cursor()
    try:
        cursor.callproc("process_semester_transition", [Data.id_student])
        db.commit()
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()
        db.close()


class CompleteCourse(BaseModel):
    id_student: int
    id_course_in_cycle: int


@app.post("/complete_course")
@require_roles(["administrator"])
async def complete_course(
    Data: CompleteCourse,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_authenticated_db),
):
    cursor = db.cursor()
    employee_id = get_employee_id_from_people_id(current_user["pid"], db)
    try:
        cursor.callproc(
            "complete_course", [Data.id_student, Data.id_course_in_cycle, employee_id]
        )
        db.commit()
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()
        db.close()


class IssueGrade(BaseModel):
    id_registration: int
    grade_value: str = Field(..., min_length=1, max_length=8)
    comment: str


@app.post("/issue_grade")
@require_roles(["administrator"])
async def issue_grade(
    Data: IssueGrade, current_user: dict = Depends(get_current_user), db = Depends(get_authenticated_db)
):
    cursor = db.cursor()
    employee_id = get_employee_id_from_people_id(current_user["pid"], db)
    try:
        cursor.callproc(
            "issue_grade",
            [Data.id_registration, employee_id, Data.grade_value, Data.comment],
        )
        db.commit()
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()
        db.close()


@app.get("/get_registrations")
@require_roles(["administrator"])
async def get_registrations(
    current_user: dict = Depends(get_current_user), db = Depends(get_authenticated_db)
):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.callproc("get_registrations")

        registrations = []
        for result in cursor.stored_results():
            registrations = result.fetchall()

        return {"registrations": registrations}
    finally:
        cursor.close()


class ApplicationSubmit(BaseModel):
    id_programme: int = Field(..., ge=0)
    motivation_letter: str


@app.post("/submit_application")
async def submit_application(
    Data: ApplicationSubmit,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_authenticated_db),
):
    cursor = db.cursor()
    try:
        cursor.callproc(
            "submit_application",
            [current_user["pid"], Data.id_programme, Data.motivation_letter],
        )
        db.commit()

        return {"status": "success", "message": "Application created"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()
        db.close()


@app.get("/get_dashboard_data")
async def get_dashboard_data(
    current_user: dict = Depends(get_current_user), db = Depends(get_authenticated_db)
):
    cursor = db.cursor()
    try:
        result_args = cursor.callproc(
            "get_dashboard_data", [current_user["pid"], False, ""]
        )

        return {"has_profile": result_args[1], "login": result_args[2]}
    finally:
        cursor.close()


@app.get("/get_available_programmes")
async def get_available_programmes(db = Depends(get_authenticated_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.callproc("get_available_programmes")

        programmes = []
        for result in cursor.stored_results():
            programmes = result.fetchall()

        return {"programmes": programmes}
    finally:
        cursor.close()


@app.get("/get_eligible_courses")
async def get_eligible_courses(
    current_user: dict = Depends(get_current_user), db = Depends(get_authenticated_db)
):
    cursor = db.cursor(dictionary=True)
    id_student = get_student_id_from_people_id(current_user["pid"], db)

    try:
        cursor.callproc("get_eligible_courses", [id_student])

        courses = []

        for result in cursor.stored_results():
            courses = result.fetchall()

        return {"eligible_courses": courses}

    finally:
        cursor.close()


@app.get("/get_current_courses")
async def get_current_courses(
    current_user: dict = Depends(get_current_user), db = Depends(get_authenticated_db)
):
    cursor = db.cursor(dictionary=True)
    id_student = get_student_id_from_people_id(current_user["pid"], db)

    try:
        cursor.callproc("get_current_courses", [id_student])

        courses = []

        for result in cursor.stored_results():
            courses = result.fetchall()

        return {"current_courses": courses}

    finally:
        cursor.close()


@app.get("/view_applications")
async def view_applications(
    current_user: dict = Depends(get_current_user), db = Depends(get_authenticated_db)
):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.callproc("view_applications", [current_user["pid"]])

        applications = []
        for result in cursor.stored_results():
            applications = result.fetchall()

        return {"applications": applications}
    finally:
        cursor.close()


def get_employee_id_from_people_id(people_id: int, db = Depends(get_authenticated_db)) -> int:
    cursor = db.cursor()
    cursor.execute("SELECT employee_id_from_people_id(%s)", (people_id,))

    result = cursor.fetchone()

    cursor.close()

    if result is None or result[0] is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return int(result[0])


def get_student_id_from_people_id(people_id: int, db = Depends(get_authenticated_db)) -> int:
    cursor = db.cursor()
    cursor.execute("SELECT student_id_from_people_id(%s)", (people_id,))

    result = cursor.fetchone()

    cursor.close()

    if result is None or result[0] is None:
        raise HTTPException(status_code=404, detail="Student not found")

    return int(result[0])


class RegisterForCourseData(BaseModel):
    course_id: int


@app.post("/register_for_course")
async def register_for_course(
    Data: RegisterForCourseData,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_authenticated_db),
):
    cursor = db.cursor()
    id_student = get_student_id_from_people_id(current_user["pid"], db)
    try:
        cursor.callproc("register_student_to_course", [id_student, Data.course_id])
        db.commit()

        return {"status": "success", "message": "Registered"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()
        db.close()
