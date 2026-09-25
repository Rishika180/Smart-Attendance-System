import { useEffect, useRef, useState } from 'react'
import Webcam from 'react-webcam'
import { markAttendance } from '../api.js'

const FRAME_WIDTH = 640
const FRAME_HEIGHT = 480
const SCAN_INTERVAL_MS = 3000

const RESULT_COLORS = {
  marked: '#22c55e',
  already_marked: '#3b82f6',
  unknown: '#ef4444',
}

const RESULT_LABELS = {
  marked: 'Marked present',
  already_marked: 'Already marked today',
  unknown: 'Unrecognized',
}

async function dataUrlToBlob(dataUrl) {
  const res = await fetch(dataUrl)
  return res.blob()
}

export default function MarkAttendance() {
  const webcamRef = useRef(null)
  const canvasRef = useRef(null)
  const [running, setRunning] = useState(false)
  const [lastResult, setLastResult] = useState(null)
  const [log, setLog] = useState([]) // recent marked-present events, most recent first
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!running) return undefined

    const intervalId = setInterval(async () => {
      const shot = webcamRef.current?.getScreenshot()
      if (!shot) return

      try {
        const blob = await dataUrlToBlob(shot)
        const res = await markAttendance(blob)
        setError(null)
        setLastResult(res.data)
        drawBoxes(res.data.recognized)

        const newlyMarked = res.data.recognized.filter((f) => f.result === 'marked')
        if (newlyMarked.length > 0) {
          setLog((prev) => [
            ...newlyMarked.map((f) => ({ name: f.name, rollNo: f.roll_no, time: new Date().toLocaleTimeString() })),
            ...prev,
          ].slice(0, 20))
        }
      } catch (err) {
        setError(err.response?.data?.detail || 'Could not reach the backend. Is it running?')
      }
    }, SCAN_INTERVAL_MS)

    return () => clearInterval(intervalId)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [running])

  const drawBoxes = (faces) => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    faces.forEach((face) => {
      const [x1, y1, x2, y2] = face.box
      const color = RESULT_COLORS[face.result] || '#ef4444'
      ctx.strokeStyle = color
      ctx.lineWidth = 2
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1)

      const label = face.name ? `${face.name} (${RESULT_LABELS[face.result]})` : 'Unknown'
      ctx.font = '14px sans-serif'
      const textWidth = ctx.measureText(label).width
      ctx.fillStyle = color
      ctx.fillRect(x1, Math.max(0, y1 - 20), textWidth + 8, 20)
      ctx.fillStyle = '#ffffff'
      ctx.fillText(label, x1 + 4, Math.max(14, y1 - 6))
    })
  }

  return (
    <div className="page">
      <h1>Mark Attendance</h1>
      <p className="subtitle">
        Point the camera at the class. Every {SCAN_INTERVAL_MS / 1000}s the frame is scanned and recognized
        students are marked present automatically.
      </p>

      <div className="attendance-grid">
        <div className="camera-panel">
          <div className="camera-overlay-wrap" style={{ width: FRAME_WIDTH, height: FRAME_HEIGHT }}>
            <Webcam
              ref={webcamRef}
              audio={false}
              screenshotFormat="image/jpeg"
              width={FRAME_WIDTH}
              height={FRAME_HEIGHT}
              screenshotWidth={FRAME_WIDTH}
              screenshotHeight={FRAME_HEIGHT}
              videoConstraints={{ width: FRAME_WIDTH, height: FRAME_HEIGHT, facingMode: 'user' }}
              className="webcam"
            />
            <canvas ref={canvasRef} width={FRAME_WIDTH} height={FRAME_HEIGHT} className="overlay-canvas" />
          </div>

          <div className="camera-actions">
            <button type="button" className={running ? 'secondary' : 'primary'} onClick={() => setRunning((r) => !r)}>
              {running ? 'Stop Scanning' : 'Start Scanning'}
            </button>
          </div>

          {error && <div className="status status-error">{error}</div>}
          {lastResult && (
            <p className="scan-summary">
              Last scan: {lastResult.faces_detected} face(s) detected.
            </p>
          )}
        </div>

        <div className="log-panel">
          <h2>Just Marked Present</h2>
          {log.length === 0 ? (
            <p className="empty-state">No one has been marked present yet this session.</p>
          ) : (
            <ul className="log-list">
              {log.map((entry, i) => (
                <li key={i}>
                  <span className="log-name">{entry.name}</span>
                  <span className="log-roll">{entry.rollNo}</span>
                  <span className="log-time">{entry.time}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}
