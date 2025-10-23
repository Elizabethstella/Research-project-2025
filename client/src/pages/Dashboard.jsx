import React, { useState } from "react";
import api from "../api";
import { FaPaperclip, FaPaperPlane, FaEye, FaEyeSlash } from "react-icons/fa";

export default function Home() {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState(null);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showSteps, setShowSteps] = useState(false);

  const sendMsg = async () => {
    if (!message) return;
    
    setLoading(true);
    setShowSteps(false);
    try {
      const res = await api.post("/solve", { question: message });
      console.log("📡 API Response:", res.data);
      
      if (res.data.success) {
        setResponse(res.data);
      } else {
        setResponse({
          error: res.data.error,
          final_answer: res.data.final_answer || "No solution available",
          solution_steps: []
        });
      }
    } catch (error) {
      console.error("Error:", error);
      setResponse({
        error: "Failed to get response. Please try again.",
        final_answer: "Sorry, I couldn't solve this problem.",
        solution_steps: []
      });
    } finally {
      setLoading(false);
      setMessage("");
    }
  };

  const uploadFile = async () => {
    if (!file) return;
    
    setLoading(true);
    setShowSteps(false);
    try {
      const formData = new FormData();
      formData.append("image", file);
      const res = await api.post("/process-image", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      
      if (res.data.success) {
        setMessage(res.data.extracted_text);
        setResponse({
          message: "Text extracted successfully! Click the send button to get help with this problem."
        });
      }
    } catch (error) {
      console.error("Error:", error);
      setResponse({
        error: "Failed to process image. Please try again."
      });
    } finally {
      setLoading(false);
      setFile(null);
    }
  };

  const toggleSteps = () => {
    setShowSteps(!showSteps);
  };

  return (
    <div className="container mt-5">
      <h2 className="text-center text-primary mb-4">Ask AS TrigTutor 🤖</h2>
      
      {/* Input Section */}
      <div className="row justify-content-center">
        <div className="col-md-8">
          <div className="card shadow-sm">
            <div className="card-body">
              <div className="input-group">
                <input 
                  value={message} 
                  onChange={e => setMessage(e.target.value)}
                  className="form-control" 
                  placeholder="Type your trigonometry question..."
                  onKeyPress={(e) => e.key === 'Enter' && sendMsg()}
                  disabled={loading}
                />
                <button 
                  className="btn btn-success" 
                  onClick={sendMsg}
                  disabled={loading || !message}
                >
                  {loading ? (
                    <div className="spinner-border spinner-border-sm" />
                  ) : (
                    <FaPaperPlane />
                  )}
                </button>
              </div>
              
              {/* File Upload */}
              <div className="mt-3 d-flex align-items-center">
                <input 
                  type="file" 
                  accept="image/*" 
                  onChange={e => setFile(e.target.files[0])}
                  className="form-control form-control-sm"
                  disabled={loading}
                />
                <button 
                  className="btn btn-outline-primary btn-sm ms-2" 
                  onClick={uploadFile}
                  disabled={loading || !file}
                >
                  <FaPaperclip /> Extract Text
                </button>
              </div>
            </div>
          </div>

          {/* Response Section */}
          {response && (
            <div className="card mt-4 shadow-sm">
              <div className="card-body">
                {response.error ? (
                  <div className="alert alert-danger">
                    <strong>Error:</strong> {response.error}
                  </div>
                ) : response.message ? (
                  <div className="alert alert-info">
                    {response.message}
                  </div>
                ) : (
                  <>
                    <h5 className="text-primary mb-3">AI Tutor Response</h5>
                    
                    {/* Final Answer - Always Visible */}
                    <div className="final-answer-section mb-4">
                      <h6 className="text-success mb-2">
                        <strong>✅ Solution:</strong>
                      </h6>
                      <div className="alert alert-success">
                        <p className="mb-0 fs-5">{response.final_answer}</p>
                      </div>
                    </div>

                    {/* Show/Hide Steps Button - Only show if there are steps */}
                    {response.solution_steps && response.solution_steps.length > 0 && (
                      <div className="mb-3">
                        <button 
                          className={`btn ${showSteps ? 'btn-outline-warning' : 'btn-outline-primary'}`}
                          onClick={toggleSteps}
                        >
                          {showSteps ? (
                            <>
                              <FaEyeSlash className="me-2" />
                              Hide Step-by-Step Solution
                            </>
                          ) : (
                            <>
                              <FaEye className="me-2" />
                              Show Step-by-Step Solution
                            </>
                          )}
                        </button>
                      </div>
                    )}

                    {/* Step-by-Step Solution - Hidden by Default */}
                    {showSteps && response.solution_steps && response.solution_steps.length > 0 && (
                      <div className="solution-steps-section mb-4">
                        <h6 className="text-secondary mb-3">📝 Step-by-Step Solution:</h6>
                        <div className="solution-steps">
                          {response.solution_steps.map((step, index) => (
                            <div key={index} className="solution-step mb-3 p-3 border rounded bg-light">
                              <div className="d-flex align-items-start">
                                <span className="badge bg-primary me-3 mt-1">{index + 1}</span>
                                <div className="step-content">
                                  {step}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Graph Image - Always Visible if Available */}
                    {response.has_graph && response.graph_image && (
                      <div className="mb-3">
                        <h6 className="text-secondary mb-2">📈 Graph:</h6>
                        <img 
                          src={response.graph_image} 
                          alt="Solution Graph" 
                          className="img-fluid rounded shadow"
                          style={{ maxHeight: '300px' }}
                        />
                      </div>
                    )}

                    {/* Disclaimer */}
                    <div className="alert alert-warning mt-3 small">
                      <strong>⚠️ Disclaimer:</strong> This AI may make mistakes. 
                      Please confirm answers with your teacher or textbook.
                    </div>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}