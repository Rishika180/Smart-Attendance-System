"""SQLAlchemy ORM models: Student and Attendance."""
from sqlalchemy import Column, Integer, String, Date, Time, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    roll_no = Column(String, unique=True, nullable=False, index=True)
    class_name = Column(String, nullable=False)
    # Average FaceNet embedding (512-d vector) stored as a JSON-encoded
    # list of floats. SQLite has no native array/vector type, and the
    # embedding is only ever read back into numpy in face_engine.py, so
    # a text column keeps things dependency-free.
    embedding = Column(Text, nullable=False)
    created_at = Column(String, nullable=False)

    attendance_records = relationship("Attendance", back_populates="student")


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (
        # A student can only be marked present once per calendar date.
        UniqueConstraint("student_id", "date", name="uq_student_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    time = Column(Time, nullable=False)
    status = Column(String, nullable=False, default="Present")

    student = relationship("Student", back_populates="attendance_records")
