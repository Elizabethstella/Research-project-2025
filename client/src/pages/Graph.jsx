import React, { useState } from "react";
import api from "../api";

export default function Graph() {
  const [expression, setExpression] = useState("sin(x)");
  const [customExpression, setCustomExpression] = useState("");
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const predefinedFunctions = [
    { value: "sin(x)", label: "sin(x)" },
    { value: "cos(x)", label: "cos(x)" },
    { value: "tan(x)", label: "tan(x)" },
    { value: "2*sin(x)", label: "2sin(x)" },
    { value: "sin(2*x)", label: "sin(2x)" },
    { value: "cos(x) + 1", label: "cos(x) + 1" }
  ];

  const handleGenerate = async (expr = null) => {
    const graphExpression = expr || expression;
    if (!graphExpression) {
      setError("Please select or enter a function");
      return;
    }

    setLoading(true);
    setError("");
    
    try {
      const res = await api.post("/generate-graph", {
        expression: graphExpression,
        question: `Graph the function: ${graphExpression}`
      });
      
      if (res.data.success && res.data.image) {
        setImage(res.data.image);
      } else {
        setError("Failed to generate graph");
      }
    } catch (err) {
      console.error("Graph generation error:", err);
      setError("Failed to generate graph. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleCustomGenerate = () => {
    if (customExpression.trim()) {
      handleGenerate(customExpression.trim());
    }
  };

  return (
    <div className="container mt-5">
      <h2 className="text-center text-primary mb-4">📈 Graph Generator</h2>
      
      <div className="row justify-content-center">
        <div className="col-md-8">
          <div className="card shadow-sm">
            <div className="card-body">
              {/* Predefined Functions */}
              <div className="mb-4">
                <label className="form-label fw-bold">Select a Function:</label>
                <div className="row g-2">
                  {predefinedFunctions.map((func, index) => (
                    <div key={index} className="col-md-4">
                      <button
                        className={`btn w-100 ${
                          expression === func.value ? 'btn-primary' : 'btn-outline-primary'
                        }`}
                        onClick={() => setExpression(func.value)}
                      >
                        {func.label}
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Custom Function Input */}
              <div className="mb-4">
                <label className="form-label fw-bold">Or Enter Custom Function:</label>
                <div className="input-group">
                  <span className="input-group-text">y =</span>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="sin(x), 2*cos(3*x), tan(x)+1, etc."
                    value={customExpression}
                    onChange={(e) => setCustomExpression(e.target.value)}
                  />
                  <button
                    className="btn btn-outline-secondary"
                    onClick={handleCustomGenerate}
                    disabled={loading || !customExpression.trim()}
                  >
                    Use Custom
                  </button>
                </div>
                <small className="text-muted">
                  Supported: sin(x), cos(x), tan(x), with coefficients and transformations
                </small>
              </div>

              {/* Generate Button */}
              <div className="text-center">
                <button
                  className="btn btn-success px-4"
                  onClick={() => handleGenerate()}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" />
                      Generating Graph...
                    </>
                  ) : (
                    "Generate Graph"
                  )}
                </button>
              </div>

              {error && (
                <div className="alert alert-danger mt-3">
                  {error}
                </div>
              )}

              {/* Graph Display */}
              {image && (
                <div className="mt-4 text-center">
                  <h5 className="text-secondary mb-3">
                    Graph of {customExpression || expression}
                  </h5>
                  <img 
                    src={image} 
                    alt="Trigonometric Graph" 
                    className="img-fluid rounded shadow"
                    style={{ maxHeight: '400px', border: '1px solid #ddd' }}
                  />
                  <div className="mt-2">
                    <button 
                      className="btn btn-outline-secondary btn-sm"
                      onClick={() => setImage(null)}
                    >
                      Clear Graph
                    </button>
                  </div>
                </div>
              )}

              {/* Instructions */}
              <div className="alert alert-info mt-4">
                <strong>💡 Tip:</strong> The graph generator can plot trigonometric functions 
                with various transformations including amplitude changes, frequency changes, 
                and vertical shifts.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}