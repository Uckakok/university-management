from fastapi import APIRouter, Depends, HTTPException
from functools import wraps
from typing import List
import mysql.connector
from models import (
    ApplicationReject,
    CompleteCourse,
    IssueGrade,
    ProcessSemesterTransition,
    ApplicationApprove,
)
from dependencies import get_authenticated_db
from auth import get_current_user
from services.db_helpers import get_employee_id_from_people_id


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


async def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "administrator":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


router = APIRouter(tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/get_applications")
async def get_applications(
    current_user: dict = Depends(get_current_user), db=Depends(get_authenticated_db)
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


@router.post("/approve_application")
async def approve_application(
    Data: ApplicationApprove,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_authenticated_db),
):
    employee_id = get_employee_id_from_people_id(current_user["pid"], db)
    cursor = db.cursor()
    try:
        cursor.callproc("approve_application", [Data.id_application, employee_id])
        db.commit()
        return {
            "status": "success",
            "message": f"Application {Data.id_application} approved",
        }
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()


@router.post("/process_semester_transition")
async def process_semester_transition(
    data: ProcessSemesterTransition,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_authenticated_db),
):
    cursor = db.cursor()
    try:
        cursor.callproc("process_semester_transition", [data.id_student])
        db.commit()
        return {
            "status": "success",
            "message": f"Semester transition processed for student {data.id_student}",
        }
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        cursor.close()


@router.post("/reject_application")
async def reject_application(
    Data: ApplicationReject,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_authenticated_db),
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


@router.post("/complete_course")
async def complete_course(
    Data: CompleteCourse,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_authenticated_db),
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


@router.post("/issue_grade")
async def issue_grade(
    Data: IssueGrade,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_authenticated_db),
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


@router.get("/get_registrations")
async def get_registrations(
    current_user: dict = Depends(get_current_user), db=Depends(get_authenticated_db)
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
        db.close()
