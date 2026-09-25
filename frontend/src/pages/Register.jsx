import { useCallback, useRef, useState } from 'react'
import Webcam from 'react-webcam'
import { registerStudent } from '../api.js'

const CAPTURES_NEEDED = 5

async function dataUrlToBlob(dataUrl) {
  const res = await fetch(dataUrl)
  return res.blob()
}

export default function Register() {
  const webcamRef = useRef(null)
  const [form, setForm] = useState({ name: '', rollNo: '', className: '' })
  const [captures, setCaptures] = useState([]) // array of data URLs (for preview)
  const [status, setStatus] = useState(null) // { type: 'success' | 'error', message }
  const [submitting, setSubmitting] = useState(false)

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const capturePhoto = useCallback(() => {
    const shot = webcamRef.current?.getScreenshot()
    if (shot && captures.length < CAPTURES_NEEDED) {
      setCaptures((prev) => [...prev, shot])
    }
  }, [captures.length])

  const resetCaptures = () => setCaptures([])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setStatus(null)

    if (!form.name || !form.rollNo || !form.className) {
      setStatus({ type: 'error', message: 'Please fill in name, roll number and class.' })
      return
    }
    if (captures.length === 0) {
      setStatus({ type: 'error', message: `Capture at least 1 photo (ideally ${CAPTURES_NEEDED}) before registering.` })
      return
    }

    setSubmitting(true)
    try {
      const blobs = await Promise.all(captures.map(dataUrlToBlob))
      const res = await registerStudent({
        name: form.name,
        rollNo: form.rollNo,
        className: form.className,
        images: blobs,
      })
      setStatus({ type: 'success', message: res.data.message })
      setForm({ name: '', rollNo: '', className: '' })
      setCaptures([])
    } catch (err) {
      const detail = err.response?.data?.detail || 'Registration failed. Is the backend running?'
      setStatus({ type: 'error', message: detail })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page">
      <h1>Register Student</h1>
      <p className="subtitle">
        Capture a few clear, front-facing photos and fill in the student's details.
      </p>

      <div className="register-grid">
        <div className="camera-panel">
          <Webcam
            ref={webcamRef}
            audio={false}
            screenshotFormat="image/jpeg"
            width={360}
            height={270}
            videoConstraints={{ width: 360, height: 270, facingMode: 'user' }}
            className="webcam"
          />
          <div className="camera-actions">
            <button type="button" onClick={capturePhoto} disabled={captures.length >= CAPTURES_NEEDED}>
              Capture Photo ({captures.length}/{CAPTURES_NEEDED})
            </button>
            <button type="button" className="secondary" onClick={resetCaptures} disabled={captures.length === 0}>
              Retake All
            </button>
          </div>
          <div className="thumbnails">
            {captures.map((src, i) => (
              <img key={i} src={src} alt={`capture ${i + 1}`} />
            ))}
          </div>
        </div>

        <form className="form-panel" onSubmit={handleSubmit}>
          <label>
            Full Name
            <input name="name" value={form.name} onChange={handleChange} placeholder="e.g. Anushka Sharma" />
          </label>
          <label>
            Roll Number
            <input name="rollNo" value={form.rollNo} onChange={handleChange} placeholder="e.g. CS21B045" />
          </label>
          <label>
            Class
            <input name="className" value={form.className} onChange={handleChange} placeholder="e.g. CSE-3A" />
          </label>

          {status && <div className={`status status-${status.type}`}>{status.message}</div>}

          <button type="submit" className="primary" disabled={submitting}>
            {submitting ? 'Registering…' : 'Register Student'}
          </button>
        </form>
      </div>
    </div>
  )
}
