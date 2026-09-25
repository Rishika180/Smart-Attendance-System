# Smart Attendance System

Face-recognition based classroom attendance system.

- **Backend:** Python, FastAPI, SQLite — face **detection** via **MTCNN** and
  **recognition** via FaceNet embeddings (both from the `facenet-pytorch`
  package, built on **OpenCV**/PIL for image handling).
- **Frontend:** **React.js** (Vite) — student registration screen, live
  attendance-marking screen, and a structured attendance-records screen.

## How it works

1. **Register a student** — capture a few webcam snapshots + name/roll
   no./class. The backend detects the face in each photo with MTCNN,
   computes a FaceNet embedding for each, and stores the average
   embedding for that student in SQLite.
2. **Mark attendance** — point a camera at the class. Every few seconds
   the current frame is sent to the backend, which detects *every* face
   in the frame, computes its embedding, and compares it against all
   registered students (Euclidean distance in embedding space). A
   confident match is marked present for today (once per student per
   day); unmatched faces are shown as "Unrecognized".
3. **Attendance records** — a table of who was marked present, filterable
   by date and class.

## Project structure

```
backend/
  app/
    main.py            FastAPI app, CORS, router wiring
    database.py         SQLite/SQLAlchemy setup
    models.py            Student, Attendance tables
    schemas.py            Pydantic request/response models
    face_engine.py         MTCNN detection + FaceNet embeddings + matching
    crud.py                  DB read/write helpers
    routers/
      students.py             POST /api/students/register, GET /api/students
      attendance.py            POST /api/attendance/mark, GET /api/attendance
  requirements.txt
frontend/
  src/
    pages/
      Register.jsx             Student registration screen
      MarkAttendance.jsx        Live camera attendance screen
      AttendanceList.jsx         Attendance records table
    components/Navbar.jsx
    api.js                        Axios calls to the backend
  package.json
```

## Running it locally

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # on Windows
# source venv/bin/activate   # on macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`. First run will download the
pretrained FaceNet weights (~100MB, cached afterward) and create
`attendance.db` automatically. Interactive API docs are at
`http://localhost:8000/docs`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Opens at `http://localhost:5173`. The browser will ask for camera
permission on the Register and Mark Attendance screens — allow it.

### Order to use it in

1. Start the backend, then the frontend.
2. Go to **Register Student**, capture ~5 photos per student, submit.
   Repeat for each student.
3. Go to **Mark Attendance**, click **Start Scanning**, point the camera
   at people. Recognized faces get boxed and marked present live.
4. Go to **Attendance Records** to see the structured log, filterable by
   date/class.

## Notes / things may want to tune

- `RECOGNITION_THRESHOLD` in `backend/app/face_engine.py` controls how
  strict matching is (lower = stricter). 0.9 is a reasonable default for
  the VGGFace2-trained FaceNet model; tune it if you see false matches
  or too many "Unrecognized" results.
- The scan interval on the Mark Attendance screen is set in
  `frontend/src/pages/MarkAttendance.jsx` (`SCAN_INTERVAL_MS`, default
  3000ms).
- CORS in `backend/app/main.py` is locked to `localhost:5173`; update it
  if you deploy the frontend elsewhere.
- This is built for a single classroom/session use case (SQLite, no
  auth) — fine for a course project or demo, not production-hardened.
