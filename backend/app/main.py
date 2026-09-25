"""FastAPI entrypoint for the Smart Attendance System backend."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine
from .routers import students, attendance

# Create all tables on startup if they don't already exist.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Attendance System API",
    description="Face-recognition based attendance backend (MTCNN detection + FaceNet embeddings).",
    version="1.0.0",
)

# The React dev server runs on a different port, so it needs CORS
# access. Tighten allow_origins before deploying anywhere public.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(students.router)
app.include_router(attendance.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
