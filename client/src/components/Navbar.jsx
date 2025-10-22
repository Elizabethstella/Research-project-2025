import React from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const token = localStorage.getItem("token");
  const user = JSON.parse(localStorage.getItem("user") || "{}");

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login");
  };

  // Don't show navbar on login/signup pages
  if (location.pathname === "/" || location.pathname === "/login" || location.pathname === "/signup") {
    return null;
  }

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
      <div className="container">
        <Link className="navbar-brand fw-bold" to="/home">
        SineWise🧠 
        </Link>
        
        <button 
          className="navbar-toggler" 
          type="button" 
          data-bs-toggle="collapse" 
          data-bs-target="#navbarNav"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto">
            {/* AI Tutor Features */}
            <li className="nav-item">
              <Link 
                className={`nav-link ${location.pathname === "/home" ? "active" : ""}`} 
                to="/home"
              >
                🤖 AI Tutor
              </Link>
            </li>
            
            {/* Learning Tools */}
            <li className="nav-item">
              <Link 
                className={`nav-link ${location.pathname === "/lesson" ? "active" : ""}`} 
                to="/lesson"
              >
                📚 Lessons
              </Link>
            </li>
            
            <li className="nav-item">
              <Link 
                className={`nav-link ${location.pathname === "/quiz" ? "active" : ""}`} 
                to="/quiz"
              >
                🧠 Quiz
              </Link>
            </li>
            
            <li className="nav-item">
              <Link 
                className={`nav-link ${location.pathname === "/graph" ? "active" : ""}`} 
                to="/graph"
              >
                📈 Graphs
              </Link>
            </li>

            {/* User Management */}
            <li className="nav-item">
              <Link 
                className={`nav-link ${location.pathname === "/dashboard" ? "active" : ""}`} 
                to="/dashboard"
              >
                📊 Dashboard
              </Link>
            </li>

            {/* Admin Only */}
            {user.role === "admin" && (
              <li className="nav-item">
                <Link 
                  className={`nav-link ${location.pathname === "/admin" ? "active" : ""}`} 
                  to="/admin"
                >
                  ⚙️ Admin
                </Link>
              </li>
            )}
          </ul>

          {/* User Info and Logout */}
          <div className="navbar-nav">
            {token ? (
              <>
                <span className="navbar-text me-3">
                  Welcome, {user.name || "Student"}!
                </span>
                <button 
                  className="btn btn-outline-light btn-sm" 
                  onClick={handleLogout}
                >
                  Logout
                </button>
              </>
            ) : (
              <Link className="nav-link" to="/login">
                Login
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}