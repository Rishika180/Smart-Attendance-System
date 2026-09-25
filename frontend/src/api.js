import axios from 'axios'

// The FastAPI backend runs on port 8000 by default (see backend/README).
export const api = axios.create({
  baseURL: 'http://localhost:8000',
})

export function registerStudent({ name, rollNo, className, images }) {
  const form = new FormData()
  form.append('name', name)
  form.append('roll_no', rollNo)
  form.append('class_name', className)
  images.forEach((blob, i) => form.append('images', blob, `capture_${i}.jpg`))

  return api.post('/api/students/register', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function getStudents() {
  return api.get('/api/students')
}

export function markAttendance(imageBlob) {
  const form = new FormData()
  form.append('image', imageBlob, 'frame.jpg')
  return api.post('/api/attendance/mark', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function getAttendance({ date, studentId, className } = {}) {
  return api.get('/api/attendance', {
    params: {
      date: date || undefined,
      student_id: studentId || undefined,
      class_name: className || undefined,
    },
  })
}
