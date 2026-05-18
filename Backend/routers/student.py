from fastapi import APIRouter, Depends, HTTPException
import mysql.connector
from models import ApplicationSubmit, CandidateRegister, RegisterForCourseData
from dependencies import get_authenticated_db
from auth import get_current_user
from services.db_helpers import get_student_id_from_people_id

router = APIRouter(tags=["student"])


async def require_student(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    return current_user


@router.post("/register_for_course")
async def register_for_course(
    Data: RegisterForCourseData,
    current_user: dict = Depends(require_student),
    db=Depends(get_authenticated_db),
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


@router.post("/submit_application")
async def submit_application(
    Data: ApplicationSubmit,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_authenticated_db),
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


@router.get("/get_dashboard_data")
async def get_dashboard_data(
    current_user: dict = Depends(get_current_user), db=Depends(get_authenticated_db)
):
    cursor = db.cursor()
    try:
        result_args = cursor.callproc(
            "get_dashboard_data", [current_user["pid"], False, ""]
        )

        return {"has_profile": result_args[1], "login": result_args[2]}
    finally:
        cursor.close()
        db.close()


@router.get("/get_available_programmes")
async def get_available_programmes(db=Depends(get_authenticated_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.callproc("get_available_programmes")

        programmes = []
        for result in cursor.stored_results():
            programmes = result.fetchall()

        return {"programmes": programmes}
    finally:
        cursor.close()
        db.close()


@router.get("/get_eligible_courses")
async def get_eligible_courses(
    current_user: dict = Depends(require_student), db=Depends(get_authenticated_db)
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
        db.close()


@router.get("/get_current_courses")
async def get_current_courses(
    current_user: dict = Depends(require_student), db=Depends(get_authenticated_db)
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
        db.close()


@router.get("/view_applications")
async def view_applications(
    current_user: dict = Depends(get_current_user), db=Depends(get_authenticated_db)
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
        db.close()


@router.post("/register_candidate")
async def register_candidate(
    Data: CandidateRegister,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_authenticated_db),
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
