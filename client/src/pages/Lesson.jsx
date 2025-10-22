import React, { useState } from "react";
import { lessonAPI } from "../services/apiService";

export default function Lesson() {
  const [topic, setTopic] = useState("");
  const [lesson, setLesson] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const topics = [
    { value: "unit circle", label: "Unit Circle" },
    { value: "sine function", label: "Sine Function" },
    { value: "cosine function", label: "Cosine Function" },
    { value: "trigonometric identities", label: "Trigonometric Identities" },
    { value: "graphing trigonometric functions", label: "Graphing Trig Functions" },
    { value: "exact values", label: "Exact Values (30°, 45°, 60°)" },
    { value: "solving equations", label: "Solving Trigonometric Equations" }
  ];

  const handleGenerate = async () => {
    if (!topic) {
      setError("Please select a topic first.");
      return;
    }

    setLoading(true);
    setError("");
    setLesson(null);

    try {
      const res = await lessonAPI.generateLesson(topic);
      
      if (res.data.error) {
        setError(res.data.error);
      } else {
        setLesson(res.data);
      }
    } catch (err) {
      console.error("API Error:", err);
      setError(
        err.response?.data?.error || 
        "Failed to generate lesson. Please check if the server is running."
      );
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="container mt-5">
      <h2 className="text-center mb-4 text-primary">📚 AI Lesson Generator</h2>

      <div className="row justify-content-center">
        <div className="col-md-8">
          <div className="card shadow-sm">
            <div className="card-body">
              <div className="text-center mb-4">
                <label htmlFor="topic-select" className="form-label fw-bold">
                  Select a Trigonometry Topic:
                </label>
                <select
                  id="topic-select"
                  className="form-select w-75 mx-auto"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  disabled={loading}
                >
                  <option value="">-- Choose a Topic --</option>
                  {topics.map((t) => (
                    <option key={t.value} value={t.value}>
                      {t.label}
                    </option>
                  ))}
                </select>

                <button
                  className="btn btn-primary mt-3 px-4"
                  onClick={handleGenerate}
                  disabled={loading || !topic}
                >
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" />
                      Generating Lesson...
                    </>
                  ) : (
                    "Generate Lesson"
                  )}
                </button>

                {error && (
                  <div className="alert alert-danger mt-3 mb-0">
                    {error}
                  </div>
                )}
              </div>

              {lesson && !lesson.error && (
                <div className="lesson-content mt-4 p-3 border rounded bg-light">
                  <div className="d-flex justify-content-between align-items-center mb-3">
                    <h4 className="text-primary mb-0">
                      {lesson.topic || "Lesson"}
                    </h4>
                    <span className="badge bg-info">
                      Confidence: {(lesson.confidence * 100).toFixed(1)}%
                    </span>
                  </div>

                  {lesson.matched_topic && lesson.matched_topic !== lesson.topic && (
                    <div className="alert alert-info py-2">
                      <small>
                        <strong>Matched to:</strong> {lesson.matched_topic}
                      </small>
                    </div>
                  )}

                  {/* Concept Explanation */}
                  {lesson.lesson_type === "concept_explanation" && (
                    <div>
                      <h5 className="text-secondary border-bottom pb-2">
                        📖 Concept Explanation
                      </h5>
                      <div className="p-3 bg-white rounded">
                        <p className="mb-0" style={{ whiteSpace: "pre-line" }}>
                          {lesson.content}
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Worked Example */}
                  {lesson.lesson_type === "worked_example" && (
                    <div>
                      <h5 className="text-secondary border-bottom pb-2">
                        📝 Worked Example: {lesson.title}
                      </h5>
                      <div className="p-3 bg-white rounded">
                        <p className="fw-bold">Question:</p>
                        <p className="mb-3">{lesson.question}</p>
                        
                        {lesson.explanation && (
                          <>
                            <p className="fw-bold">Explanation:</p>
                            <p className="mb-3">{lesson.explanation}</p>
                          </>
                        )}

                        {lesson.solution?.length > 0 && (
                          <>
                            <p className="fw-bold">Step-by-Step Solution:</p>
                            <ol className="ps-3">
                              {lesson.solution.map((step, i) => (
                                <li key={i} className="mb-2">
                                  {step}
                                </li>
                              ))}
                            </ol>
                          </>
                        )}

                        {lesson.difficulty && (
                          <p className="text-muted mb-0">
                            <strong>Difficulty:</strong> {lesson.difficulty}
                          </p>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Practice Exercise */}
                  {lesson.lesson_type === "practice_exercise" && (
                    <div>
                      <h5 className="text-secondary border-bottom pb-2">
                        🏋️ Practice Exercise
                      </h5>
                      <div className="p-3 bg-white rounded">
                        <p className="fw-bold">Question:</p>
                        <p className="mb-3">{lesson.question}</p>

                        {lesson.solution?.length > 0 && (
                          <>
                            <p className="fw-bold">Solution:</p>
                            <ol className="ps-3">
                              {lesson.solution.map((step, i) => (
                                <li key={i} className="mb-2">
                                  {step}
                                </li>
                              ))}
                            </ol>
                          </>
                        )}

                        {lesson.final_answer && (
                          <p className="fw-bold text-success">
                            Final Answer: {lesson.final_answer}
                          </p>
                        )}

                        {lesson.difficulty && (
                          <p className="text-muted">
                            <strong>Difficulty:</strong> {lesson.difficulty}
                          </p>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="mt-3 pt-2 border-top">
                    <small className="text-muted">
                      <strong>Source:</strong> {lesson.source}
                    </small>
                    <br />
                    <small className="text-muted">
                      ⚠️ <strong>Disclaimer:</strong> AI-generated content. 
                      Always verify with your teacher or textbook.
                    </small>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}