import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import MarkAttendance from './pages/MarkAttendance.jsx'
import Register from './pages/Register.jsx'
import AttendanceList from './pages/AttendanceList.jsx'

export default function App() {
  return (
    <div className="app">
      <Navbar />
      <main className="content">
        <Routes>
          <Route path="/" element={<MarkAttendance />} />
          <Route path="/register" element={<Register />} />
          <Route path="/attendance" element={<AttendanceList />} />
        </Routes>
      </main>
    </div>
  )
}
