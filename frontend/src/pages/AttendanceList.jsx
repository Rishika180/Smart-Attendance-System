import { useEffect, useState } from 'react'
import { getAttendance, getStudents } from '../api.js'

function todayISO() {
  return new Date().toISOString().slice(0, 10)
}

export default function AttendanceList() {
  const [date, setDate] = useState(todayISO())
  const [classFilter, setClassFilter] = useState('')
  const [records, setRecords] = useState([])
  const [classes, setClasses] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    getStudents()
      .then((res) => {
        const unique = [...new Set(res.data.map((s) => s.class_name))].sort()
        setClasses(unique)
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    setError(null)
    getAttendance({ date: date || undefined, className: classFilter || undefined })
      .then((res) => setRecords(res.data))
      .catch(() => setError('Could not load attendance records. Is the backend running?'))
      .finally(() => setLoading(false))
  }, [date, classFilter])

  return (
    <div className="page">
      <h1>Attendance Records</h1>
      <p className="subtitle">Structured, filterable view of everyone marked present.</p>

      <div className="filters">
        <label>
          Date
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        </label>
        <label>
          Class
          <select value={classFilter} onChange={(e) => setClassFilter(e.target.value)}>
            <option value="">All classes</option>
            {classes.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
        {date && (
          <button type="button" className="secondary" onClick={() => setDate('')}>
            Clear date filter
          </button>
        )}
      </div>

      {error && <div className="status status-error">{error}</div>}

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Roll No.</th>
              <th>Class</th>
              <th>Date</th>
              <th>Time</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="empty-state">
                  Loading…
                </td>
              </tr>
            ) : records.length === 0 ? (
              <tr>
                <td colSpan={6} className="empty-state">
                  No attendance records for this filter.
                </td>
              </tr>
            ) : (
              records.map((r) => (
                <tr key={r.id}>
                  <td>{r.student_name}</td>
                  <td>{r.roll_no}</td>
                  <td>{r.class_name}</td>
                  <td>{r.date}</td>
                  <td>{r.time}</td>
                  <td>
                    <span className="badge">{r.status}</span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
