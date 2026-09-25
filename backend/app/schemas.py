"""Pydantic request/response schemas."""
from datetime import date as date_type, time as time_type
from pydantic import BaseModel, ConfigDict


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    roll_no: str
    class_name: str
    created_at: str


class StudentRegisterResponse(BaseModel):
    student: StudentOut
    faces_used: int
    message: str


class AttendanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date_type
    time: time_type
    status: str
    student_id: int
    student_name: str
    roll_no: str
    class_name: str


class RecognizedFace(BaseModel):
    box: list[int]  # [x1, y1, x2, y2]
    student_id: int | None = None
    name: str | None = None
    roll_no: str | None = None
    confidence: float
    result: str  # "marked" | "already_marked" | "unknown"


class MarkAttendanceResponse(BaseModel):
    faces_detected: int
    recognized: list[RecognizedFace]
