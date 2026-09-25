"""Attendance marking and lookup endpoints."""
from datetime import date as date_type

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from .. import crud, face_engine, schemas
from ..database import get_db

router = APIRouter(prefix="/api/attendance", tags=["attendance"])


@router.post("/mark", response_model=schemas.MarkAttendanceResponse)
async def mark_attendance(
    image: UploadFile = File(..., description="A single camera frame, possibly containing several faces"),
    db: Session = Depends(get_db),
):
    content = await image.read()
    try:
        pil_image = face_engine.bytes_to_pil(content)
    except Exception:
        raise HTTPException(status_code=422, detail="Could not read the uploaded image")

    detections = face_engine.detect_and_embed_all(pil_image)
    known_students = crud.list_known_embeddings(db)

    recognized = []
    for box, embedding in detections:
        match, distance = face_engine.find_best_match(embedding, known_students)
        confidence = 0.0 if distance is None else max(0.0, 1.0 - distance / face_engine.RECOGNITION_THRESHOLD)

        if match is None:
            recognized.append(
                schemas.RecognizedFace(box=box, confidence=round(confidence, 2), result="unknown")
            )
            continue

        record, created = crud.mark_attendance(db, match["id"])
        recognized.append(
            schemas.RecognizedFace(
                box=box,
                student_id=match["id"],
                name=match["name"],
                roll_no=match["roll_no"],
                confidence=round(confidence, 2),
                result="marked" if created else "already_marked",
            )
        )

    return schemas.MarkAttendanceResponse(faces_detected=len(detections), recognized=recognized)


@router.get("", response_model=list[schemas.AttendanceOut])
def get_attendance(
    date: date_type | None = Query(None, description="Filter to a single date, defaults to all dates"),
    student_id: int | None = Query(None),
    class_name: str | None = Query(None),
    db: Session = Depends(get_db),
):
    records = crud.query_attendance(db, date=date, student_id=student_id, class_name=class_name)
    return [
        schemas.AttendanceOut(
            id=r.id,
            date=r.date,
            time=r.time,
            status=r.status,
            student_id=r.student_id,
            student_name=r.student.name,
            roll_no=r.student.roll_no,
            class_name=r.student.class_name,
        )
        for r in records
    ]
