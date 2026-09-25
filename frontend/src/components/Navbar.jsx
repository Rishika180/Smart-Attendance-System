import { NavLink } from 'react-router-dom'

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand">Smart Attendance System</div>
      <div className="navbar-links">
        <NavLink to="/" end className={({ isActive }) => (isActive ? 'active' : '')}>
          Mark Attendance
        </NavLink>
        <NavLink to="/register" className={({ isActive }) => (isActive ? 'active' : '')}>
          Register Student
        </NavLink>
        <NavLink to="/attendance" className={({ isActive }) => (isActive ? 'active' : '')}>
          Attendance Records
        </NavLink>
      </div>
    </nav>
  )
}
