"""Database read/write helpers used by the API routers."""
from datetime import datetime, date as date_type

from sqlalchemy.orm import Session

from . import models, face_engine


def create_student(db: Session, name: str, roll_no: str, class_name: str, embedding) -> models.Student:
    student = models.Student(
        name=name,
        roll_no=roll_no,
        class_name=class_name,
        embedding=face_engine.embedding_to_json(embedding),
        created_at=datetime.utcnow().isoformat(),
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def get_student_by_roll_no(db: Session, roll_no: str) -> models.Student | None:
    return db.query(models.Student).filter(models.Student.roll_no == roll_no).first()


def list_students(db: Session) -> list[models.Student]:
    return db.query(models.Student).order_by(models.Student.name).all()


def list_known_embeddings(db: Session) -> list[dict]:
    """All registered students with their embedding decoded to a numpy array,
    ready for face_engine.find_best_match()."""
    students = db.query(models.Student).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "roll_no": s.roll_no,
            "class_name": s.class_name,
            "embedding": face_engine.json_to_embedding(s.embedding),
        }
        for s in students
    ]


def get_attendance_today(db: Session, student_id: int, today: date_type) -> models.Attendance | None:
    return (
        db.query(models.Attendance)
        .filter(models.Attendance.student_id == student_id, models.Attendance.date == today)
        .first()
    )


def mark_attendance(db: Session, student_id: int) -> tuple[models.Attendance, bool]:
    """Mark a student present for today. Returns (record, created) where
    created=False means the student was already marked present today."""
    now = datetime.now()
    today = now.date()

    existing = get_attendance_today(db, student_id, today)
    if existing:
        return existing, False

    record = models.Attendance(
        student_id=student_id,
        date=today,
        time=now.time().replace(microsecond=0),
        status="Present",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record, True


def query_attendance(db: Session, date: date_type | None, student_id: int | None, class_name: str | None):
    q = db.query(models.Attendance).join(models.Student)
    if date is not None:
        q = q.filter(models.Attendance.date == date)
    if student_id is not None:
        q = q.filter(models.Attendance.student_id == student_id)
    if class_name is not None:
        q = q.filter(models.Student.class_name == class_name)
    return q.order_by(models.Attendance.date.desc(), models.Attendance.time.desc()).all()
