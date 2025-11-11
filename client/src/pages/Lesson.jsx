import React, { useState, useEffect } from "react";
import { lessonAPI } from "../services/apiService";
import { detectTopicFromQuestion, getTopicDisplayName } from "../utils/topicDetector";

export default function Lessons() {
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const [question, setQuestion] = useState("");
  const [conversation, setConversation] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const savedConversation = localStorage.getItem(`user_${user.id}_conversation`);
    if (savedConversation) {
      try {
        setConversation(JSON.parse(savedConversation));
      } catch (error) {
        console.error("Error loading conversation:", error);
      }
    }
  }, [user.id]);

  // Save conversation to localStorage whenever it changes
  useEffect(() => {
    if (conversation.length > 0) {
      localStorage.setItem(`user_${user.id}_conversation`, JSON.stringify(conversation));
    }
  }, [conversation, user.id]);

  // Function to detect if question is trigonometry-related
  const isTrigonometryQuestion = (question) => {
    const trigKeywords = [
      // Basic trig functions
      'sin', 'cos', 'tan', 'sine', 'cosine', 'tangent',
      'csc', 'sec', 'cot', 'cosec', 'secant', 'cotangent',
      
      // Inverse trig functions
      'arcsin', 'arccos', 'arctan', 'asin', 'acos', 'atan',
      
      // Trig identities and equations
      'trigonometry', 'trigonometric', 'identity', 'identities',
      'equation', 'solve', 'prove', 'verify',
      
      // Angles and measurements
      'angle', 'degree', 'radian', 'π', 'pi',
      'triangle', 'right triangle', 'hypotenuse', 'opposite', 'adjacent',
      
      // Graphs and properties
      'graph', 'amplitude', 'period', 'frequency', 'phase', 'shift',
      'wave', 'oscillation', 'periodic',
      
      // Applications
      'sine rule', 'cosine rule', 'law of sines', 'law of cosines',
      'bearing', 'elevation', 'depression', 'height', 'distance',
      
      // Special angles and values
      'unit circle', 'special angles', 'exact values',
      '30°', '45°', '60°', '90°', '180°', '360°',
      
      // Trigonometric formulas
      'double angle', 'half angle', 'sum to product', 'product to sum',
      'addition formula', 'subtraction formula',
      
      // Common symbols
      'θ', 'α', 'β', 'γ', '°'
    ];

    const questionLower = question.toLowerCase();
    
    // Check for trig keywords
    const hasTrigKeyword = trigKeywords.some(keyword => 
      questionLower.includes(keyword.toLowerCase())
    );

    // Check for math symbols and patterns
    const hasTrigPattern = 
      /sin|cos|tan|θ|π|°/.test(questionLower) ||
      /trig|triangle|angle/.test(questionLower) ||
      /solve.*sin|solve.*cos|solve.*tan/.test(questionLower) ||
      /graph.*sin|graph.*cos|graph.*tan/.test(questionLower);

    return hasTrigKeyword || hasTrigPattern;
  };

  const parseAIResponse = (response) => {
    const sections = {
      explanation: "",
      stepByStep: [],
      practice: "",
      concepts: [],
      tips: [],
      workedExample: {}
    };

    try {
      // If the response is already JSON, parse it directly
      if (response.trim().startsWith('{') && response.trim().endsWith('}')) {
        try {
          const jsonResponse = JSON.parse(response);
          return {
            explanation: jsonResponse.explanation || "",
            stepByStep: Array.isArray(jsonResponse.steps) ? jsonResponse.steps : [],
            practice: jsonResponse.worked_example?.problem || "",
            concepts: jsonResponse.key_concepts || [],
            tips: jsonResponse.examination_tips || [],
            workedExample: {
              problem: jsonResponse.worked_example?.problem || "",
              solution: Array.isArray(jsonResponse.worked_example?.solution) ? 
                       jsonResponse.worked_example.solution : 
                       (jsonResponse.worked_example?.solution ? [jsonResponse.worked_example.solution] : [])
            }
          };
        } catch (e) {
          // If JSON parsing fails, fall through to text parsing
        }
      }

      // Text-based parsing with multiple fallback patterns
      const lines = response.split('\n').map(line => line.trim()).filter(line => line.length > 0);
      
      let currentSection = 'explanation';
      let sectionContent = {
        explanation: [],
        stepByStep: [],
        practice: [],
        concepts: [],
        tips: []
      };

      // Common section headers to look for
      const sectionHeaders = [
        { pattern: /step-by-step|step by step|solution:/i, key: 'stepByStep' },
        { pattern: /practice|example|problem:/i, key: 'practice' },
        { pattern: /concepts|key concepts|syllabus concepts/i, key: 'concepts' },
        { pattern: /tips|examination tips|advice/i, key: 'tips' },
        { pattern: /worked example|example problem/i, key: 'practice' }
      ];

      for (const line of lines) {
        // Check if this line is a section header
        let isHeader = false;
        for (const header of sectionHeaders) {
          if (header.pattern.test(line)) {
            currentSection = header.key;
            isHeader = true;
            break;
          }
        }

        if (!isHeader) {
          // Add content to current section
          if (line && !line.match(/^\*+$/) && !line.match(/^[-*]\s*$/)) {
            sectionContent[currentSection].push(line);
          }
        }
      }

      // Process each section
      sections.explanation = sectionContent.explanation.join('\n');
      
      // Step-by-step: look for numbered steps or bullet points
      const stepLines = sectionContent.stepByStep.filter(line => 
        /^\d+[\.\)]|^step\s*\d+|^[-*]\s/.test(line.toLowerCase())
      );
      sections.stepByStep = stepLines.length > 0 ? stepLines : sectionContent.stepByStep;
      
      // Practice/problem section
      sections.practice = sectionContent.practice.join('\n');
      
      // Concepts - look for comma-separated or bullet points
      if (sectionContent.concepts.length > 0) {
        const conceptText = sectionContent.concepts.join(' ');
        sections.concepts = conceptText.split(/[,•]|\band\b/)
          .map(concept => concept.trim())
          .filter(concept => concept.length > 0 && !concept.match(/^concepts?$/i));
      }
      
      // Tips - look for bullet points or numbered tips
      sections.tips = sectionContent.tips.filter(tip => 
        tip.length > 10 && !tip.match(/^tips?$/i)
      );

      // Try to extract worked example from practice section
      if (sections.practice) {
        const problemMatch = sections.practice.match(/(?:problem|question)[:\s]*(.*?)(?=solution|$)/is);
        const solutionMatch = sections.practice.match(/(?:solution|answer)[:\s]*(.*)/is);
        
        if (problemMatch || solutionMatch) {
          sections.workedExample = {
            problem: problemMatch ? problemMatch[1].trim() : sections.practice,
            solution: solutionMatch ? [solutionMatch[1].trim()] : []
          };
        }
      }

      // Fallback: if no structured content found, use everything as explanation
      if (!sections.explanation && !sections.stepByStep.length && response) {
        sections.explanation = response;
      }

    } catch (error) {
      console.error("Error parsing AI response:", error);
      // Fallback: use the raw response as explanation
      sections.explanation = response;
    }

    return sections;
  };

  const handleAskQuestion = async (e) => {
    e.preventDefault();
    
    if (!question.trim()) {
      setError("Please enter a question");
      return;
    }

    if (!user?.id) {
      setError("Please log in to ask questions");
      return;
    }

    // Check if question is trigonometry-related
    if (!isTrigonometryQuestion(question)) {
      setError("I only answer trigonometry-related questions. Please ask about sine, cosine, tangent, angles, triangles, or other trigonometry topics.");
      
      // Add error message to conversation
      const errorMessage = {
        type: "error",
        content: "I specialize in trigonometry questions only. Please ask me about trigonometric functions, identities, equations, graphs, or triangle problems.",
        timestamp: new Date().toISOString()
      };
      
      setConversation(prev => [...prev, errorMessage]);
      return;
    }

    setLoading(true);
    setError("");

    try {
      const detectedTopic = detectTopicFromQuestion(question);
      const topicDisplayName = getTopicDisplayName(detectedTopic);
      // Add user's question to conversation
      const userMessage = {
        type: "user",
        content: question,
        detectedTopic: detectedTopic,
        topicDisplayName: topicDisplayName,
        timestamp: new Date().toISOString()
      };

      const updatedConversation = [...conversation, userMessage];
      setConversation(updatedConversation);
      
      console.log(`Detected topic: ${detectedTopic} (${topicDisplayName}) for question: "${question}"`);
      // Send question to backend
      const res = await lessonAPI.askQuestion(
        detectedTopic,// Use valid topic ID
        question,
        updatedConversation.filter(msg => msg.type === "user").map(msg => msg.content),
        user.id
      );

      console.log("Raw AI Response:", res.data.response); // Debug log

      // Parse the AI response into structured format
      const parsedResponse = parseAIResponse(res.data.response);

      console.log("Parsed Response:", parsedResponse); // Debug log

      // Add AI response to conversation
      const aiMessage = {
        type: "ai",
        content: res.data.response, // Keep original for fallback
        parsedContent: parsedResponse,
        hasGraph: res.data.has_graph,
        graphImage: res.data.graph_image,
        keyConcepts: res.data.key_concepts || [],
        examinationTips: res.data.examination_tips || [],
        workedExample: res.data.worked_example || {},
        timestamp: new Date().toISOString()
      };

      setConversation(prev => [...prev, aiMessage]);
      setQuestion(""); // Clear input after successful submission

    } catch (error) {
      console.error("Error asking question:", error);
      setError("Failed to get answer. Please try again.");
      
      // Add error message to conversation
      const errorMessage = {
        type: "error",
        content: "Sorry, I couldn't process your question. Please try again.",
        timestamp: new Date().toISOString()
      };
      
      setConversation(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const clearConversation = () => {
    setConversation([]);
    localStorage.removeItem(`user_${user.id}_conversation`);
    setError("");
  };

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    const conversationContainer = document.querySelector('.conversation-container');
    if (conversationContainer) {
      conversationContainer.scrollTop = conversationContainer.scrollHeight;
    }
  }, [conversation]);

  // Component for rendering formatted AI response
  const FormattedAIResponse = ({ message }) => {
    const { parsedContent, content, workedExample, keyConcepts, examinationTips } = message;
    
    // Use parsed content if available, otherwise fallback to original
    const data = parsedContent || {
      explanation: content,
      stepByStep: [],
      practice: "",
      concepts: keyConcepts || [],
      tips: examinationTips || [],
      workedExample: workedExample || {}
    };

    // Safely handle stepByStep - it could be string, array, or undefined
    const stepsToDisplay = (() => {
      if (Array.isArray(data.stepByStep)) {
        return data.stepByStep;
      } else if (typeof data.stepByStep === 'string') {
        // Split string by newlines and filter out empty lines
        return data.stepByStep.split('\n')
          .map(step => step.trim())
          .filter(step => step.length > 0);
      } else {
        return [];
      }
    })();

    // Filter out empty sections
    const hasExplanation = data.explanation && data.explanation.length > 10;
    const hasSteps = stepsToDisplay.length > 0;
    const hasPractice = data.practice && data.practice.length > 0;
    const hasConcepts = data.concepts && data.concepts.length > 0;
    const hasTips = data.tips && data.tips.length > 0;
    const hasWorkedExample = data.workedExample && (data.workedExample.problem || data.workedExample.solution);

    // If no structured content was parsed, show the raw content
    if (!hasExplanation && !hasSteps && !hasPractice && !hasConcepts && !hasTips && !hasWorkedExample && content) {
      return (
        <div className="ai-response-content">
          <div className="explanation-section">
            <div className="explanation-text bg-light p-3 rounded">
              {content.split('\n').map((paragraph, idx) => (
                <p key={idx} className={idx > 0 ? 'mt-2 mb-0' : 'mb-0'}>
                  {paragraph}
                </p>
              ))}
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="ai-response-content">
        {/* Explanation */}
        {hasExplanation && (
          <div className="explanation-section mb-4">
            <div className="section-header d-flex align-items-center mb-2">
              <i className="fas fa-graduation-cap text-primary me-2"></i>
              <h6 className="mb-0">Explanation</h6>
            </div>
            <div className="explanation-text bg-light p-3 rounded">
              {data.explanation.split('\n').map((paragraph, idx) => (
                <p key={idx} className={idx > 0 ? 'mt-2 mb-0' : 'mb-0'}>
                  {paragraph}
                </p>
              ))}
            </div>
          </div>
        )}

        {/* Step-by-Step Solution */}
        {hasSteps && (
          <div className="steps-section mb-4">
            <div className="section-header d-flex align-items-center mb-2">
              <i className="fas fa-list-ol text-success me-2"></i>
              <h6 className="mb-0">Step-by-Step Solution</h6>
            </div>
            <div className="steps-content bg-white border border-success border-opacity-25 p-3 rounded">
              {stepsToDisplay.map((step, idx) => (
                <div key={idx} className="step-item d-flex align-items-start mb-2">
                  <span className="badge bg-success me-2 mt-1">{idx + 1}</span>
                  <span className="flex-grow-1">
                    {typeof step === 'string' ? step.replace(/^Step\s*\d+:\s*/, '') : String(step)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Worked Example */}
        {(data.workedExample?.problem || workedExample?.problem) && (
          <div className="example-section mb-4">
            <div className="section-header d-flex align-items-center mb-2">
              <i className="fas fa-pencil-alt text-warning me-2"></i>
              <h6 className="mb-0">Worked Example</h6>
            </div>
            <div className="example-content bg-warning bg-opacity-10 p-3 rounded">
              <div className="problem mb-3">
                <strong>Problem: </strong>
                {data.workedExample?.problem || workedExample?.problem}
              </div>
              {(data.workedExample?.solution || workedExample?.solution) && (
                <div className="solution">
                  <strong>Solution: </strong>
                  {Array.isArray(data.workedExample?.solution || workedExample?.solution) ? (
                    <ol className="mt-2 mb-0">
                      {(data.workedExample?.solution || workedExample?.solution).map((step, idx) => (
                        <li key={idx} className="mb-1">{step}</li>
                      ))}
                    </ol>
                  ) : (
                    <p className="mt-2 mb-0">{data.workedExample?.solution || workedExample?.solution}</p>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Practice Problem */}
        {hasPractice && !hasWorkedExample && (
          <div className="practice-section mb-4">
            <div className="section-header d-flex align-items-center mb-2">
              <i className="fas fa-pencil-alt text-warning me-2"></i>
              <h6 className="mb-0">Practice Problem</h6>
            </div>
            <div className="practice-content bg-warning bg-opacity-10 p-3 rounded">
              {data.practice.split('\n').map((paragraph, idx) => (
                <p key={idx} className={idx > 0 ? 'mt-2 mb-0' : 'mb-0'}>
                  {paragraph}
                </p>
              ))}
            </div>
          </div>
        )}

        {/* Key Concepts */}
        {(data.concepts.length > 0 || keyConcepts.length > 0) && (
          <div className="concepts-section mb-4">
            <div className="section-header d-flex align-items-center mb-2">
              <i className="fas fa-key text-info me-2"></i>
              <h6 className="mb-0">Key Concepts</h6>
            </div>
            <div className="concepts-content">
              {(data.concepts.length > 0 ? data.concepts : keyConcepts).map((concept, idx) => (
                <span key={idx} className="badge bg-info me-1 mb-1">
                  {concept}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Examination Tips */}
        {(data.tips.length > 0 || examinationTips.length > 0) && (
          <div className="tips-section">
            <div className="section-header d-flex align-items-center mb-2">
              <i className="fas fa-lightbulb text-warning me-2"></i>
              <h6 className="mb-0">Examination Tips</h6>
            </div>
            <div className="tips-content">
              <ul className="list-unstyled mb-0">
                {(data.tips.length > 0 ? data.tips : examinationTips).map((tip, idx) => (
                  <li key={idx} className="d-flex align-items-start mb-1">
                    <i className="fas fa-chevron-right text-warning me-2 mt-1 small"></i>
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Syllabus Alignment Badge */}
        <div className="syllabus-badge mt-3 pt-3 border-top">
          <small className="text-muted">
            <i className="fas fa-certificate me-1"></i>
            Aligned with Namibia NSSCAS Mathematics Syllabus 8227
          </small>
        </div>
      </div>
    );
  };

  return (
    <div className="lessons-page">
      <div className="container mt-4">
        <div className="row justify-content-center">
          <div className="col-lg-10 col-xl-8">
            {/* Header */}
            <div className="text-center mb-4">
              <h2>NSSCAS AI Tutor</h2>
              <p className="text-muted">
                AI tutor may make mistakes!
              </p>
              
              {/* Conversation Stats */}
              {conversation.length > 0 && (
                <div className="d-flex justify-content-center align-items-center gap-3 mt-2">
                  <span className="badge bg-primary">
                    {conversation.filter(msg => msg.type === 'user').length} questions asked
                  </span>
                  <button
                    type="button"
                    className="btn btn-outline-danger btn-sm"
                    onClick={clearConversation}
                  >
                    <i className="fas fa-trash me-1"></i>
                    Clear All
                  </button>
                </div>
              )}
            </div>

            {/* Question Input */}
            <div className="card mb-4 shadow-sm">
              <div className="card-body">
                <form onSubmit={handleAskQuestion}>
                  <div className="mb-3">
                    <label htmlFor="question" className="form-label">
                      <strong>Your Question:</strong>
                    </label>
                    {/* Math Symbol Input */}
<div className="mb-3">
  <label className="form-label">
    <strong>Math Symbols:</strong>
  </label>
  <div className="math-symbols d-flex flex-wrap gap-2 mb-2">
    {['θ', 'π', 'α', 'β', 'γ', '°', '√', '²', '³', '∫', '∑', '∞', '≠', '≈', '≤', '≥', '±', '÷', '×'].map((symbol) => (
      <button
        key={symbol}
        type="button"
        className="btn btn-outline-secondary btn-sm"
        onClick={() => setQuestion(prev => prev + symbol)}
        title={`Insert ${symbol}`}
      >
        {symbol}
      </button>
    ))}
  </div>
  
  <textarea
    id="question"
    className="form-control"
    rows="3"
    placeholder="e.g., Can you explain how to solve trigonometric equations? Or help me understand radians? How do I prove trigonometric identities?"
    value={question}
    onChange={(e) => setQuestion(e.target.value)}
    disabled={loading}
  />
</div>
                    
                    <div className="form-text">
                      Ask anything about Trigonometry.
                    </div>
                  </div>
                  
                  {error && (
                    <div className="alert alert-danger" role="alert">
                      <i className="fas fa-exclamation-triangle me-2"></i>
                      {error}
                    </div>
                  )}

                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      {conversation.length > 0 && (
                        <span className="text-muted small">
                          <i className="fas fa-save me-1"></i>
                          Conversation saved automatically
                        </span>
                      )}
                    </div>
                    
                    <button
                      type="submit"
                      className="btn btn-primary px-4"
                      disabled={!question.trim() || loading}
                    >
                      {loading ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          Thinking...
                        </>
                      ) : (
                        <>
                          <i className="fas fa-paper-plane me-2"></i>
                          Ask Question
                        </>
                      )}
                    </button>
                  </div>
                </form>
              </div>
            </div>

            {/* Conversation */}
            <div className="conversation-container" style={{ maxHeight: '70vh', overflowY: 'auto' }}>
              {conversation.length === 0 ? (
                <div className="text-center py-5">
                  <div className="text-muted">
                    <i className="fas fa-comments fa-3x mb-3 text-primary"></i>
                    <h5>Start a Conversation</h5>
                    <p>No questions yet. Ask me anything about Trigometry!</p>
                    <div className="mt-3">
                      <small className="d-block"><strong>Example questions:</strong></small>
                      <small className="text-muted">
                        "How do I convert degrees to radians?"<br/>
                        "Explain trigonometric identities"<br/>
                        "Help me solve sin(x) = 0.5"<br/>
                        "What's the difference between sine and cosine graphs?"
                      </small>
                    </div>
                  </div>
                </div>
              ) : (
                conversation.map((message, index) => (
                  <div key={index} className={`message ${message.type} mb-4`}>
                    {message.type === "user" && (
                      <div className="d-flex justify-content-end">
                        <div className="user-message bg-primary text-white p-3 rounded-3" style={{ maxWidth: '80%' }}>
                          <div className="message-content">
                            <div className="d-flex align-items-center mb-1">
                              <i className="fas fa-user me-2 small"></i>
                              <small className="opacity-75">You</small>
                                {message.topicDisplayName && (
                        <small className="opacity-75 ms-2 badge bg-light text-dark">
                       <i className="fas fa-tag me-1"></i>
                          {message.topicDisplayName}
                               </small>
                             )}
                               </div>
                         
                            {message.content}
                          </div>
                          <small className="opacity-75 d-block mt-2 text-end">
                            {new Date(message.timestamp).toLocaleTimeString([], { 
                              hour: '2-digit', 
                              minute: '2-digit' 
                            })}
                          </small>
                        </div>
                      </div>
                    )}

                    {message.type === "ai" && (
                      <div className="d-flex justify-content-start">
                        <div className="ai-message bg-light border p-3 rounded-3" style={{ maxWidth: '90%' }}>
                          <div className="message-content">
                            <div className="d-flex align-items-center mb-3">
                              <i className="fas fa-robot me-2 text-primary"></i>
                              <small className="text-muted">Math Assistant</small>
                            </div>
                            
                            <FormattedAIResponse message={message} />
                            
                            {/* Graph if available */}
                            {message.hasGraph && message.graphImage && (
                              <div className="mt-4 text-center">
                                <div className="border rounded p-2 bg-white">
                                  <img 
                                    src={message.graphImage} 
                                    alt="Graph visualization" 
                                    className="img-fluid rounded"
                                    style={{ maxHeight: "250px" }}
                                  />
                                  <small className="text-muted d-block mt-1">Graph Visualization</small>
                                </div>
                              </div>
                            )}
                          </div>
                          <small className="text-muted d-block mt-3 pt-2 border-top">
                            {new Date(message.timestamp).toLocaleTimeString([], { 
                              hour: '2-digit', 
                              minute: '2-digit' 
                            })}
                          </small>
                        </div>
                      </div>
                    )}

                    {message.type === "error" && (
                      <div className="d-flex justify-content-start">
                        <div className="error-message bg-danger text-white p-3 rounded-3" style={{ maxWidth: '80%' }}>
                          <div className="message-content">
                            <div className="d-flex align-items-center mb-1">
                              <i className="fas fa-exclamation-triangle me-2"></i>
                              <small>System</small>
                            </div>
                            {message.content}
                          </div>
                          <small className="opacity-75 d-block mt-2">
                            {new Date(message.timestamp).toLocaleTimeString([], { 
                              hour: '2-digit', 
                              minute: '2-digit' 
                            })}
                          </small>
                        </div>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}