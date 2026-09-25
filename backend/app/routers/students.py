"""Student registration endpoints."""
import numpy as np
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .. import crud, face_engine, schemas
from ..database import get_db

router = APIRouter(prefix="/api/students", tags=["students"])


@router.post("/register", response_model=schemas.StudentRegisterResponse)
async def register_student(
    name: str = Form(...),
    roll_no: str = Form(...),
    class_name: str = Form(...),
    images: list[UploadFile] = File(..., description="A few webcam snapshots of the student's face"),
    db: Session = Depends(get_db),
):
    if crud.get_student_by_roll_no(db, roll_no):
        raise HTTPException(status_code=409, detail=f"Roll no '{roll_no}' is already registered")

    embeddings = []
    for image in images:
        content = await image.read()
        try:
            pil_image = face_engine.bytes_to_pil(content)
        except Exception:
            continue  # skip unreadable frames rather than failing the whole registration
        embedding = face_engine.get_single_embedding(pil_image)
        if embedding is not None:
            embeddings.append(embedding)

    if not embeddings:
        raise HTTPException(
            status_code=422,
            detail="No face could be detected in any of the submitted images. Please retake the photos with better lighting and a clear, front-facing view.",
        )

    # Average all valid embeddings into one representative vector for the student.
    average_embedding = np.mean(embeddings, axis=0)

    student = crud.create_student(db, name=name, roll_no=roll_no, class_name=class_name, embedding=average_embedding)

    return schemas.StudentRegisterResponse(
        student=schemas.StudentOut.model_validate(student),
        faces_used=len(embeddings),
        message=f"Registered {student.name} using {len(embeddings)} of {len(images)} captured photos.",
    )


@router.get("", response_model=list[schemas.StudentOut])
def get_students(db: Session = Depends(get_db)):
    return crud.list_students(db)
