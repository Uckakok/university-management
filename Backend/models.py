from pydantic import BaseModel, Field, EmailStr, BeforeValidator
from typing import Optional, Annotated
from enum import Enum


def empty_to_none(v: str | None) -> str | None:
    if v == "" or (isinstance(v, str) and not v.strip()):
        return None
    return v


class GenderEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"
    PREFER_NOT_TO_SAY = "Prefer not to say"


class UserRegister(BaseModel):
    name: str = Field(..., min_length=3, max_length=64)
    second_name: Annotated[Optional[str], BeforeValidator(empty_to_none)] = Field(
        None, min_length=3, max_length=64
    )
    surname: str = Field(..., min_length=3, max_length=64)
    gender: GenderEnum
    login: str = Field(..., min_length=3, max_length=32)
    password: str


class CandidateRegister(BaseModel):
    nationality: str = Field(..., min_length=2, max_length=2, pattern=r"^[A-Z]{2}$")
    pesel: str = Field(..., min_length=11, max_length=11, pattern=r"^\d{11}$")
    email_address: EmailStr
    phone_number: str = Field(..., pattern=r"^\+?[\d\s\-]{7,15}$")
    address: str = Field(..., min_length=5, max_length=255)


class ApplicationSubmit(BaseModel):
    id_programme: int = Field(..., ge=0)
    motivation_letter: str


class ProcessSemesterTransition(BaseModel):
    id_student: int = Field(..., gt=0)


class RegisterForCourseData(BaseModel):
    course_id: int


class ApplicationReject(BaseModel):
    id_application: int


class ApplicationApprove(BaseModel):
    id_application: int


class CompleteCourse(BaseModel):
    id_student: int
    id_course_in_cycle: int


class IssueGrade(BaseModel):
    id_registration: int
    grade_value: str = Field(..., min_length=1, max_length=8)
    comment: str
