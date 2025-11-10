// Login.jsx
import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { authAPI } from "../services/apiService";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [forgotPasswordLoading, setForgotPasswordLoading] = useState(false);
  const [forgotPasswordSuccess, setForgotPasswordSuccess] = useState("");
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const navigate = useNavigate();

  const validateForm = () => {
    if (!email.trim()) {
      setError("Email is required");
      return false;
    }
    
    if (!/\S+@\S+\.\S+/.test(email)) {
      setError("Please enter a valid email address");
      return false;
    }
    
    if (!password && !showForgotPassword) {
      setError("Password is required");
      return false;
    }
    
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setForgotPasswordSuccess("");

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const res = await authAPI.login(email, password);
      
      // Store token and user data
      localStorage.setItem("token", res.data.token);
      localStorage.setItem("user", JSON.stringify(res.data.user));
      
      navigate("/lesson");
    } catch (err) {
      console.error("Login error:", err);
      const errorMessage = err.response?.data?.error || 
                          err.response?.data?.message || 
                          "Login failed. Please check your credentials and try again.";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = async () => {
    if (!email.trim()) {
      setError("Please enter your email address to reset password");
      return;
    }

    if (!/\S+@\S+\.\S+/.test(email)) {
      setError("Please enter a valid email address");
      return;
    }

    setForgotPasswordLoading(true);
    setError("");
    setForgotPasswordSuccess("");

    try {
      await authAPI.forgotPassword(email);
      setForgotPasswordSuccess("Password reset instructions have been sent to your email.");
      setShowForgotPassword(false);
    } catch (err) {
      console.error("Forgot password error:", err);
      const errorMessage = err.response?.data?.error || 
                          err.response?.data?.message || 
                          "Failed to send reset instructions. Please try again.";
      setError(errorMessage);
    } finally {
      setForgotPasswordLoading(false);
    }
  };

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card shadow">
            <div className="card-body">
              <h2 className="text-center text-primary mb-4">Login to AS TrigTutor</h2>
              
              {error && (
                <div className="alert alert-danger">
                  <i className="bi bi-exclamation-triangle me-2"></i>
                  {error}
                </div>
              )}
              
              {forgotPasswordSuccess && (
                <div className="alert alert-success">
                  <i className="bi bi-check-circle me-2"></i>
                  {forgotPasswordSuccess}
                </div>
              )}
              
              {!showForgotPassword ? (
                <form onSubmit={handleSubmit}>
                  <div className="mb-3">
                    <label className="form-label">Email</label>
                    <input
                      type="email"
                      className="form-control"
                      placeholder="Enter your email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                  
                  <div className="mb-3">
                    <label className="form-label">Password</label>
                    <input
                      type="password"
                      className="form-control"
                      placeholder="Enter your password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                  </div>
                  
                  <div className="mb-3 text-end">
                    <button 
                      type="button" 
                      className="btn btn-link p-0 text-decoration-none"
                      onClick={() => setShowForgotPassword(true)}
                    >
                      Forgot your password?
                    </button>
                  </div>
                  
                  <button 
                    className="btn btn-primary w-100" 
                    type="submit"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Logging in...
                      </>
                    ) : (
                      "Login"
                    )}
                  </button>
                </form>
              ) : (
                <div>
                  <div className="mb-3">
                    <label className="form-label">Enter your email to reset password</label>
                    <input
                      type="email"
                      className="form-control"
                      placeholder="Enter your email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                  
                  <div className="d-flex gap-2">
                    <button 
                      className="btn btn-primary flex-fill" 
                      onClick={handleForgotPassword}
                      disabled={forgotPasswordLoading}
                    >
                      {forgotPasswordLoading ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2"></span>
                          Sending...
                        </>
                      ) : (
                        "Send Reset Instructions"
                      )}
                    </button>
                    
                    <button 
                      className="btn btn-outline-secondary" 
                      onClick={() => setShowForgotPassword(false)}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
              
              <p className="mt-3 text-center">
                No account? <Link to="/signup">Sign up here</Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}