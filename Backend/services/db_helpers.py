from fastapi import Depends, HTTPException
from dependencies import get_authenticated_db


def get_employee_id_from_people_id(
    people_id: int, db=Depends(get_authenticated_db)
) -> int:
    with db.cursor() as cursor:
        cursor.execute("SELECT employee_id_from_people_id(%s)", (people_id,))
        result = cursor.fetchone()

    if result is None or result[0] is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return int(result[0])


def get_student_id_from_people_id(
    people_id: int, db=Depends(get_authenticated_db)
) -> int:
    with db.cursor() as cursor:
        cursor.execute("SELECT student_id_from_people_id(%s)", (people_id,))
        result = cursor.fetchone()

    if result is None or result[0] is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return int(result[0])
