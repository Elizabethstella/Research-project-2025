import React, { useState, useEffect } from "react";
import { quizAPI } from "../services/apiService";

export default function Quiz() {
  const [topic, setTopic] = useState("");
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(false);
  // ... rest of your Quiz.jsx component

  const handleGenerate = async () => {
    if (!topic) return;
    
    setLoading(true);
    try {
      const res = await quizAPI.generateQuiz(topic, 5);
      setQuiz(res.data);
      // ... rest of your quiz logic
    } catch (error) {
      console.error("Error generating quiz:", error);
      alert(error.response?.data?.error || "Failed to generate quiz. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // ... rest of your Quiz.jsx component


  // Countdown timer effect
  useEffect(() => {
    if (!quiz || Object.keys(countdowns).length === 0) return;

    const timer = setInterval(() => {
      setCountdowns(prev => {
        const newCountdowns = { ...prev };
        let anyActive = false;

        Object.keys(newCountdowns).forEach(qId => {
          if (newCountdowns[qId] > 0) {
            newCountdowns[qId]--;
            anyActive = true;
          } else if (newCountdowns[qId] === 0 && !availableAnswers[qId]) {
            // Time's up - mark answer as available
            setAvailableAnswers(prev => ({ ...prev, [qId]: true }));
            fetchAnswer(qId);
          }
        });

        if (!anyActive) {
          clearInterval(timer);
        }
        return newCountdowns;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [quiz, countdowns, availableAnswers]);

  const fetchAnswer = async (questionId) => {
    try {
      const res = await api.post("/quiz-question-answer", {
        quiz_id: quiz.quiz_id,
        question_id: questionId
      });
      
      if (res.data.answer_available) {
        setAvailableAnswers(prev => ({ 
          ...prev, 
          [questionId]: res.data 
        }));
      }
    } catch (error) {
      console.error("Error fetching answer:", error);
    }
  };

  const handleAnswerChange = (questionId, value) => {
    setAnswers(prev => ({ ...prev, [questionId]: value }));
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const checkAnswerAvailability = async (questionId) => {
    try {
      const res = await api.post("/quiz-question-answer", {
        quiz_id: quiz.quiz_id,
        question_id: questionId
      });
      
      if (res.data.answer_available) {
        setAvailableAnswers(prev => ({ 
          ...prev, 
          [questionId]: res.data 
        }));
      } else {
        alert(`Answer available in ${res.data.time_remaining_display}`);
      }
    } catch (error) {
      console.error("Error checking answer:", error);
    }
  };

  return (
    <div className="container mt-5">
      <h2 className="text-center text-primary mb-4">🧠 Trigonometry Quiz</h2>
      
      {/* Topic Selection */}
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card shadow-sm">
            <div className="card-body text-center">
              <h5 className="mb-3">Select Quiz Topic</h5>
              <select
                className="form-select mb-3"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                disabled={loading}
              >
                <option value="">-- Choose a Topic --</option>
                {topics.map((t, index) => (
                  <option key={index} value={t}>
                    {t.charAt(0).toUpperCase() + t.slice(1)}
                  </option>
                ))}
              </select>
              
              <button 
                className="btn btn-primary w-100"
                onClick={handleGenerate}
                disabled={loading || !topic}
              >
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" />
                    Generating Quiz...
                  </>
                ) : (
                  "Generate Quiz"
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Quiz Content */}
      {quiz && (
        <div className="card mt-4 shadow-sm">
          <div className="card-header bg-primary text-white">
            <h4 className="mb-0">
              {quiz.topic} Quiz 
              <span className="badge bg-light text-primary ms-2">
                {quiz.total_questions} Questions
              </span>
            </h4>
            <small>Total Duration: {quiz.total_duration_display}</small>
          </div>
          
          <div className="card-body">
            <div className="alert alert-info">
              <strong>Instructions:</strong> {quiz.instructions}
            </div>

            {quiz.questions.map((question) => (
              <div key={question.id} className="card mb-4">
                <div className="card-header d-flex justify-content-between align-items-center">
                  <div>
                    <strong>Question {question.id}</strong>
                    <span className={`badge ms-2 ${
                      question.difficulty === 'easy' ? 'bg-success' :
                      question.difficulty === 'medium' ? 'bg-warning' : 'bg-danger'
                    }`}>
                      {question.difficulty}
                    </span>
                  </div>
                  
                  <div className={`timer ${countdowns[question.id] < 60 ? 'text-danger' : 'text-success'}`}>
                    ⏱️ {formatTime(countdowns[question.id] || 0)}
                  </div>
                </div>
                
                <div className="card-body">
                  <p className="fw-bold">{question.question}</p>
                  
                  {/* Answer Input */}
                  <div className="mb-3">
                    <label className="form-label">Your Answer:</label>
                    <input
                      type="text"
                      className="form-control"
                      value={answers[question.id] || ""}
                      onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                      placeholder="Enter your solution..."
                    />
                  </div>

                  {/* Answer Display */}
                  {availableAnswers[question.id] && (
                    <div className="alert alert-success">
                      <h6>✅ Answer:</h6>
                      <p><strong>Final Answer:</strong> {availableAnswers[question.id].final_answer}</p>
                      
                      {availableAnswers[question.id].solution_steps && (
                        <div>
                          <strong>Step-by-Step Solution:</strong>
                          <ol className="mt-2">
                            {availableAnswers[question.id].solution_steps.map((step, index) => (
                              <li key={index}>{step}</li>
                            ))}
                          </ol>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Check Answer Button */}
                  {!availableAnswers[question.id] && (
                    <button
                      className="btn btn-outline-primary btn-sm"
                      onClick={() => checkAnswerAvailability(question.id)}
                    >
                      Check if Answer is Available
                    </button>
                  )}
                </div>
              </div>
            ))}

            <div className="text-center">
              <button className="btn btn-success">
                Submit Quiz
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}