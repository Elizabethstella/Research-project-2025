import React, { useState, useEffect } from "react";
import { lessonAPI } from "../services/apiService";

export default function GenerateLesson() {
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState("");
  const [currentSection, setCurrentSection] = useState(0);
  const [lessonContent, setLessonContent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [studentProgress, setStudentProgress] = useState({});
  const [showAnswers, setShowAnswers] = useState({});
  const [completedTopics, setCompletedTopics] = useState({});

  // Load topics and student progress on component mount
  useEffect(() => {
    loadTopics();
    loadStudentProgress();
    loadCompletedTopics();
  }, [user.id]);

  const loadTopics = async () => {
    try {
      const response = await lessonAPI.getTopics();
      setTopics(response.data.topics || []);
    } catch (error) {
      console.error("Error loading topics:", error);
      setError("Failed to load topics");
    }
  };

  const loadStudentProgress = () => {
    try {
      const savedProgress = localStorage.getItem(`user_${user.id}_lesson_progress`);
      if (savedProgress) {
        const progress = JSON.parse(savedProgress);
        setStudentProgress(progress);
        
        // If there's an active topic, load it
        if (progress.activeTopic) {
          setSelectedTopic(progress.activeTopic);
          setCurrentSection(progress.currentSection || 0);
        }
      }
    } catch (error) {
      console.error("Error loading progress:", error);
    }
  };

  const loadCompletedTopics = () => {
    try {
      const savedCompleted = localStorage.getItem(`user_${user.id}_completed_topics`);
      if (savedCompleted) {
        setCompletedTopics(JSON.parse(savedCompleted));
      }
    } catch (error) {
      console.error("Error loading completed topics:", error);
    }
  };

  const saveStudentProgress = (topicId, sectionIndex) => {
    const progress = {
      activeTopic: topicId,
      currentSection: sectionIndex,
      lastAccessed: new Date().toISOString()
    };
    
    setStudentProgress(progress);
    localStorage.setItem(`user_${user.id}_lesson_progress`, JSON.stringify(progress));
  };

  const markTopicAsCompleted = (topicId) => {
    const updatedCompleted = {
      ...completedTopics,
      [topicId]: {
        completed: true,
        completedAt: new Date().toISOString()
      }
    };
    
    setCompletedTopics(updatedCompleted);
    localStorage.setItem(`user_${user.id}_completed_topics`, JSON.stringify(updatedCompleted));
    
    // Clear progress for this topic
    const progress = { ...studentProgress };
    if (progress.activeTopic === topicId) {
      delete progress.activeTopic;
      delete progress.currentSection;
      setStudentProgress(progress);
      localStorage.setItem(`user_${user.id}_lesson_progress`, JSON.stringify(progress));
    }
  };

  const startLesson = async (topicId) => {
    if (!topicId) {
      setError("Please select a topic");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await lessonAPI.startTopic(user.id, topicId);
      
      if (response.data.success) {
        setLessonContent(response.data.lesson_content);
        setSelectedTopic(topicId);
        setCurrentSection(0);
        saveStudentProgress(topicId, 0);
        
      } else {
        setError(response.data.error || "Failed to start lesson");
      }
    } catch (error) {
      console.error("Error starting lesson:", error);
      setError("Failed to start lesson. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const continueLesson = async () => {
    if (!selectedTopic) return;

    setLoading(true);
    setError("");

    try {
      const response = await lessonAPI.continueTopic(user.id, selectedTopic);
      
      if (response.data.success) {
        setLessonContent(response.data.lesson_content);
        // Keep the current section from progress
      } else {
        setError(response.data.error || "Failed to continue lesson");
      }
    } catch (error) {
      console.error("Error continuing lesson:", error);
      setError("Failed to continue lesson. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const completeLesson = async () => {
  if (!selectedTopic) return;

  setLoading(true);
  setError("");

  try {
    // Check if completeTopic function exists in the API
    if (lessonAPI.completeTopic && typeof lessonAPI.completeTopic === 'function' && !usingFallbackTopics) {
      const response = await lessonAPI.completeTopic(user.id, selectedTopic);
      if (!response.data.success) {
        setError(response.data.error || "Failed to complete lesson");
        return;
      }
    }
    // If API doesn't have completeTopic or we're using fallback, just mark as completed locally
      
    // Mark as completed locally
    markTopicAsCompleted(selectedTopic);
    
    // Show success message
    setError(""); // Clear any previous errors
    
    // Reset lesson state
    setLessonContent(null);
    setSelectedTopic("");
    
    // Optional: Show a temporary success message
    const successMessage = "Lesson completed successfully! 🎉";
    setError(successMessage);
    
    // Clear success message after 3 seconds
    setTimeout(() => setError(""), 3000);
    
  } catch (error) {
    console.error("Error completing lesson:", error);
    
    // Even if API fails, mark as completed locally
    markTopicAsCompleted(selectedTopic);
    
    // Show success message for local completion
    const successMessage = "Lesson marked as completed! 🎉";
    setError(successMessage);
    
    // Clear success message after 3 seconds
    setTimeout(() => setError(""), 3000);
    
    // Reset lesson state
    setLessonContent(null);
    setSelectedTopic("");
  } finally {
    setLoading(false);
  }
};
  const loadSection = async (sectionIndex) => {
    if (!selectedTopic) return;

    setLoading(true);
    setError("");

    try {
      const response = await lessonAPI.getLessonSection(user.id, selectedTopic, sectionIndex);
      
      if (response.data.success) {
        setLessonContent(response.data.lesson_content);
        setCurrentSection(sectionIndex);
        saveStudentProgress(selectedTopic, sectionIndex);
      } else {
        setError(response.data.error || "Failed to load section");
      }
    } catch (error) {
      console.error("Error loading section:", error);
      setError("Failed to load lesson section. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const getTopicProgress = (topicId) => {
    if (studentProgress.activeTopic === topicId) {
      return {
        currentSection: studentProgress.currentSection || 0,
        hasProgress: true
      };
    }
    return { currentSection: 0, hasProgress: false };
  };

  const isTopicCompleted = (topicId) => {
    return completedTopics[topicId]?.completed || false;
  };

  const isLastSection = () => {
    return lessonContent && currentSection === lessonContent.total_sections - 1;
  };

  const renderLessonContent = () => {
    if (!lessonContent) return null;

    const section = lessonContent.current_section;
    const lastSection = isLastSection();

    return (
      <div className="lesson-content">
        {/* Lesson Header */}
        <div className="lesson-header bg-primary text-white p-4 rounded-top">
          <div className="d-flex justify-content-between align-items-start">
            <div>
              <h3 className="mb-1">{lessonContent.title}</h3>
              <p className="mb-0 opacity-75">{lessonContent.description}</p>
            </div>
            <div className="text-end">
              <div className="badge bg-light text-primary fs-6">
                Section {currentSection + 1} of {lessonContent.total_sections}
              </div>
              {lessonContent.ai_generated && (
                <div className="badge bg-success mt-1">
                  <i className="fas fa-robot me-1"></i>
                  AI Generated
                </div>
              )}
              {lastSection && (
                <div className="badge bg-warning mt-1">
                  <i className="fas fa-flag-checkered me-1"></i>
                  Final Section
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="progress-bar-section bg-light p-3 border-bottom">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <small className="text-muted">Progress</small>
            <small className="text-muted">
              {Math.round((currentSection / lessonContent.total_sections) * 100)}%
            </small>
          </div>
          <div className="progress" style={{ height: "8px" }}>
            <div 
              className="progress-bar" 
              style={{ 
                width: `${(currentSection / lessonContent.total_sections) * 100}%` 
              }}
            ></div>
          </div>
        </div>

        {/* Section Navigation */}
        <div className="section-navigation bg-light p-3 border-bottom">
          <div className="d-flex justify-content-between align-items-center">
            <button
              className="btn btn-outline-primary btn-sm"
              disabled={currentSection === 0}
              onClick={() => loadSection(currentSection - 1)}
            >
              <i className="fas fa-chevron-left me-1"></i>
              Previous
            </button>
            
            <div className="section-dots">
              {Array.from({ length: lessonContent.total_sections }, (_, i) => (
                <button
                  key={i}
                  className={`btn btn-sm mx-1 ${
                    i === currentSection 
                      ? 'btn-primary' 
                      : i < currentSection 
                        ? 'btn-success' 
                        : 'btn-outline-secondary'
                  }`}
                  onClick={() => loadSection(i)}
                  disabled={loading}
                >
                  {i + 1}
                </button>
              ))}
            </div>

            {lastSection ? (
              <button
                className="btn btn-success btn-sm"
                onClick={completeLesson}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                    Completing...
                  </>
                ) : (
                  <>
                    <i className="fas fa-check me-1"></i>
                    Complete Lesson
                  </>
                )}
              </button>
            ) : (
              <button
                className="btn btn-primary btn-sm"
                onClick={() => loadSection(currentSection + 1)}
              >
                Next
                <i className="fas fa-chevron-right ms-1"></i>
              </button>
            )}
          </div>
        </div>

        {/* Learning Objectives */}
        {lessonContent.learning_objectives && lessonContent.learning_objectives.length > 0 && (
          <div className="learning-objectives p-4 border-bottom">
            <h5 className="text-primary mb-3">
              <i className="fas fa-bullseye me-2"></i>
              Learning Objectives
            </h5>
            <ul className="list-unstyled mb-0">
              {lessonContent.learning_objectives.map((objective, index) => (
                <li key={index} className="d-flex align-items-start mb-2">
                  <i className="fas fa-check text-success mt-1 me-2"></i>
                  <span>{objective}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Main Content */}
        <div className="main-content p-4">
          <h4 className="text-primary mb-4">{section.title}</h4>

          {/* Content Points */}
          {section.content && section.content.length > 0 && (
            <div className="content-points mb-4">
              {section.content.map((point, index) => (
                <div key={index} className="content-point card mb-3">
                  <div className="card-body">
                    <div className="d-flex align-items-start">
                      <span className="badge bg-primary me-3 mt-1">{index + 1}</span>
                      <div className="flex-grow-1">
                        {point}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Worked Examples */}
          {section.worked_examples && section.worked_examples.length > 0 && (
            <div className="worked-examples mb-4">
              <h5 className="text-success mb-3">
                <i className="fas fa-calculator me-2"></i>
                Worked Examples
              </h5>
              {section.worked_examples.map((example, index) => (
                <div key={index} className="worked-example card border-success mb-3">
                  <div className="card-header bg-success text-white">
                    <strong>Example {index + 1}</strong>
                  </div>
                  <div className="card-body">
                    <div className="problem mb-3">
                      <strong>Problem: </strong>
                      {example.problem}
                    </div>
                    <div className="solution">
                      <strong>Solution: </strong>
                      {example.solution}
                    </div>
                    {example.explanation && (
                      <div className="explanation mt-2 p-2 bg-light rounded">
                        <strong>Explanation: </strong>
                        {example.explanation}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Practice Questions */}
          {section.practice_questions && section.practice_questions.length > 0 && (
            <div className="practice-questions">
              <h5 className="text-warning mb-3">
                <i className="fas fa-pencil-alt me-2"></i>
                Practice Questions
              </h5>
              {section.practice_questions.map((question, index) => (
                <div key={index} className="practice-question card border-warning mb-3">
                  <div className="card-header bg-warning text-dark">
                    <strong>Question {index + 1}</strong>
                  </div>
                  <div className="card-body">
                    <div className="question mb-3">
                      <strong>Q: </strong>
                      {question.question}
                    </div>
                    {question.hint && (
                      <div className="hint mb-2 p-2 bg-light rounded">
                        <strong>Hint: </strong>
                        {question.hint}
                      </div>
                    )}
                    <div className="answer">
                      <strong>Answer: </strong>
                      {question.answer}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Syllabus Alignment */}
        {lessonContent.syllabus_alignment && (
          <div className="syllabus-alignment bg-light p-4 border-top">
            <h6 className="text-primary mb-3">
              <i className="fas fa-certificate me-2"></i>
              Namibia Syllabus Alignment
            </h6>
            <div className="row">
              <div className="col-md-6">
                <strong>Covered Objectives:</strong>
                <ul className="mb-0 mt-2">
                  {lessonContent.syllabus_alignment.covered_objectives?.map((obj, idx) => (
                    <li key={idx}>{obj}</li>
                  ))}
                </ul>
              </div>
              <div className="col-md-6">
                <strong>Assessment Preparation:</strong>
                <p className="mb-0 mt-2">
                  {lessonContent.syllabus_alignment.assessment_preparation}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="generate-lesson-page">
      <div className="container mt-4">
        <div className="row justify-content-center">
          <div className="col-lg-10 col-xl-8">
            {/* Header */}
            <div className="text-center mb-4">
              <h2>Generate Lesson</h2>
              <p className="text-muted">
                Choose a trigonometry topic and AI will generate a structured lesson from basic to advanced concepts.
              </p>
            </div>

            {/* Topic Selection */}
            <div className="card mb-4 shadow-sm">
              <div className="card-body">
                <h5 className="card-title mb-3">
                  <i className="fas fa-book me-2 text-primary"></i>
                  Select a Topic
                </h5>
                
                {error && (
                  <div className="alert alert-danger" role="alert">
                    <i className="fas fa-exclamation-triangle me-2"></i>
                    {error}
                  </div>
                )}

                <div className="row">
                  {topics.map((topic) => {
                    const progress = getTopicProgress(topic.id);
                    const isCompleted = isTopicCompleted(topic.id);
                    
                    return (
                      <div key={topic.id} className="col-md-6 mb-3">
                        <div 
                          className={`topic-card card h-100 cursor-pointer ${
                            selectedTopic === topic.id ? 'border-primary' : ''
                          } ${isCompleted ? 'border-success' : ''}`}
                          onClick={() => !loading && setSelectedTopic(topic.id)}
                          style={{ cursor: 'pointer' }}
                        >
                          <div className="card-body">
                            <div className="d-flex justify-content-between align-items-start mb-2">
                              <h6 className="card-title mb-0">
                                <span className="me-2">{topic.icon}</span>
                                {topic.name}
                                {isCompleted && (
                                  <i className="fas fa-check-circle text-success ms-2" title="Completed"></i>
                                )}
                              </h6>
                              {progress.hasProgress && !isCompleted && (
                                <span className="badge bg-success">
                                  {progress.currentSection + 1}/{topic.total_sections}
                                </span>
                              )}
                              {isCompleted && (
                                <span className="badge bg-success">
                                  <i className="fas fa-check me-1"></i>
                                  Completed
                                </span>
                              )}
                            </div>
                            <p className="card-text small text-muted">
                              {topic.description}
                            </p>
                            <div className="topic-meta">
                              <small className="text-muted">
                                <i className="fas fa-clock me-1"></i>
                                {topic.estimated_time} • 
                                <i className="fas fa-signal ms-2 me-1"></i>
                                {topic.difficulty}
                              </small>
                            </div>
                          </div>
                          <div className="card-footer bg-transparent">
                            {selectedTopic === topic.id ? (
                              <div className="d-grid gap-2">
                                {isCompleted ? (
                                  <button
                                    className="btn btn-outline-primary btn-sm"
                                    onClick={() => startLesson(topic.id)}
                                    disabled={loading}
                                  >
                                    <i className="fas fa-redo me-1"></i>
                                    Restart Lesson
                                  </button>
                                ) : progress.hasProgress ? (
                                  <>
                                    <button
                                      className="btn btn-primary btn-sm"
                                      onClick={() => continueLesson()}
                                      disabled={loading}
                                    >
                                      {loading ? (
                                        <>
                                          <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                                          Loading...
                                        </>
                                      ) : (
                                        <>
                                          <i className="fas fa-play me-1"></i>
                                          Continue Lesson
                                        </>
                                      )}
                                    </button>
                                    <button
                                      className="btn btn-outline-secondary btn-sm"
                                      onClick={() => startLesson(topic.id)}
                                      disabled={loading}
                                    >
                                      <i className="fas fa-redo me-1"></i>
                                      Restart
                                    </button>
                                  </>
                                ) : (
                                  <button
                                    className="btn btn-primary btn-sm"
                                    onClick={() => startLesson(topic.id)}
                                    disabled={loading}
                                  >
                                    {loading ? (
                                      <>
                                        <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                                        Starting...
                                      </>
                                    ) : (
                                      <>
                                        <i className="fas fa-play me-1"></i>
                                        Start Lesson
                                      </>
                                    )}
                                  </button>
                                )}
                              </div>
                            ) : (
                              <button
                                className="btn btn-outline-primary btn-sm w-100"
                                onClick={() => setSelectedTopic(topic.id)}
                              >
                                Select Topic
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {topics.length === 0 && !loading && (
                  <div className="text-center py-4">
                    <div className="text-muted">
                      <i className="fas fa-book fa-3x mb-3"></i>
                      <p>No topics available at the moment.</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Lesson Content */}
            {lessonContent && renderLessonContent()}

            {/* Empty State */}
            {!lessonContent && selectedTopic && (
              <div className="text-center py-5">
                <div className="text-muted">
                  <i className="fas fa-chalkboard-teacher fa-3x mb-3"></i>
                  <h5>Ready to Learn</h5>
                  <p>Select a topic above to generate your AI-powered lesson.</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}