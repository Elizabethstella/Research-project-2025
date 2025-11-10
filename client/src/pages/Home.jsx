import React, { useState, useEffect } from "react";
import api from "../api";
import { FaPaperPlane, FaUpload, FaCalculator, FaVideo, FaEye, FaEyeSlash, FaPlus, FaTrash, FaHistory } from "react-icons/fa";

export default function Home() {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState(null);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showSteps, setShowSteps] = useState(false);
  const [showMathKeyboard, setShowMathKeyboard] = useState(false);
  const [showVideoDropdown, setShowVideoDropdown] = useState(false);
  const [conversation, setConversation] = useState([]); // For current chat
  const [conversations, setConversations] = useState([]); // For conversation list
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [showSidebar, setShowSidebar] = useState(true);
  const [chatHistory, setChatHistory] = useState([]);

  const mathSymbols = [
    "π", "θ", "α", "β", "°", "√", "²", "³", "∫", "∑",
    "∞", "±", "≠", "≈", "≤", "≥", "(", ")", "[", "]",
    "sin", "cos", "tan", "cot", "sec", "csc",
    "log", "ln", "x", "y", "=", "+", "-", "*", "/"
  ];

  const videoTopics = {
    "identities": "https://youtube.com/playlist?list=PLQhErzEfXXbXQ4RK8ztQgl13Vwqx5FaVN&si=YK-g26e-8fAn39-K",
    "equations": "https://youtube.com/playlist?list=PLQhErzEfXXbXQ4RK8ztQgl13Vwqx5FaVN&si=YK-g26e-8fAn39-K",
    "fundamentals": "https://youtube.com/playlist?list=PLQhErzEfXXbXQ4RK8ztQgl13Vwqx5FaVN&si=YK-g26e-8fAn39-K"
  };

  // Load conversations on component mount
  useEffect(() => {
    loadConversations();
    createNewConversation(); // Start with a new conversation
  }, []);

  const loadConversations = async () => {
    try {
      const res = await api.get("/conversations");
      setConversations(res.data.conversations || []);
    } catch (error) {
      console.error("Error loading conversations:", error);
    }
  };

  // Add this missing function
  const switchConversation = async (conversationId) => {
    try {
      setCurrentConversationId(conversationId);
      // Clear current chat history when switching conversations
      setChatHistory([]);
      
      // In a real app, you would load the conversation messages here
      // For now, we'll just set a loading state and clear the chat
      setLoading(true);
      
      // Simulate loading conversation messages
      setTimeout(() => {
        setLoading(false);
      }, 500);
      
    } catch (error) {
      console.error("Error switching conversation:", error);
      setLoading(false);
    }
  };

  const createNewConversation = async () => {
    try {
      // Create conversation locally without API call
      const conversationId = `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      const welcomeMessage = {
        type: 'ai',
        content: {
          final_answer: "Welcome to SineWise! I'm your AI trigonometry Solver. Ask me a trigonometry question, and I'll help you solve it step by step."
        },
        timestamp: new Date()
      };
      
      // Set both conversation and chat history
      setConversation([welcomeMessage]);
      setChatHistory([welcomeMessage]);
      setCurrentConversationId(conversationId);
      
      // Add to conversations list
      setConversations(prev => [...prev, {
        id: conversationId,
        message_count: 1,
        created_at: new Date().toISOString()
      }]);
      
      return conversationId;
      
    } catch (error) {
      console.error("Error creating conversation:", error);
      // Fallback: still set the welcome message even if there's an error
      const fallbackMessage = {
        type: 'ai',
        content: {
          final_answer: "Welcome! Ask me any trigonometry question.",
        },
        timestamp: new Date()
      };
      setConversation([fallbackMessage]);
      setChatHistory([fallbackMessage]);
    }
  };

  // Remove or comment out these functions since they reference undefined 'user' variable
  /*
  const saveConversation = (conversationId, messages) => {
    localStorage.setItem(`user_${user.id}_conversation_${conversationId}`, JSON.stringify(messages));
  };

  const getUserConversations = () => {
    const conversations = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(`user_${user.id}_conversation_`)) {
        const conversationId = key.replace(`user_${user.id}_conversation_`, '');
        conversations.push(conversationId);
      }
    }
    return conversations;
  };
  */

  const deleteConversation = async (conversationId) => {
    try {
      // Handle deletion locally without API call
      setConversations(prev => prev.filter(conv => conv.id !== conversationId));
      if (currentConversationId === conversationId) {
        setCurrentConversationId(null);
        // Clear the current conversation
        setConversation([]);
        setChatHistory([]);
      }
    } catch (error) {
      console.error("Error deleting conversation:", error);
      // Even if there's an error, we can still update the local state
      setConversations(prev => prev.filter(conv => conv.id !== conversationId));
      if (currentConversationId === conversationId) {
        setCurrentConversationId(null);
        setConversation([]);
        setChatHistory([]);
      }
    }
  };

  const insertSymbol = (symbol) => {
    setMessage(prev => prev + symbol);
  };

  const sendMsg = async () => {
    if (!message.trim()) return;
    
    setLoading(true);
    
    // Add user message to chat history
    const userMessage = { type: 'user', content: message, timestamp: new Date() };
    setChatHistory(prev => [...prev, userMessage]);
    
    try {
      const requestData = { question: message };
      if (currentConversationId) {
        requestData.conversation_id = currentConversationId;
      }
      
      const res = await api.post("/solve", requestData);
      
      // Add AI response to chat history
      const aiMessage = { 
        type: 'ai', 
        content: res.data,
        timestamp: new Date(),
        showSteps: false // Initially hide steps
      };
      setChatHistory(prev => [...prev, aiMessage]);
      setResponse(res.data);

      // Update conversation ID if returned
      if (res.data.conversation_id && res.data.conversation_id !== currentConversationId) {
        setCurrentConversationId(res.data.conversation_id);
      }

      // Reload conversations to update counts
      await loadConversations();
    } catch (error) {
      console.error("Error:", error);
      const errorMessage = { 
        type: 'ai', 
        content: { error: "Failed to get response. Please try again." },
        timestamp: new Date()
      };
      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      setMessage("");
    }
  };

  const toggleSteps = (index) => {
    const newHistory = [...chatHistory];
    newHistory[index].showSteps = !newHistory[index].showSteps;
    setChatHistory(newHistory);
  };

  const formatConversationId = (convId) => {
    if (!convId) return "New Chat";
    const parts = convId.split('_');
    return parts.length > 1 ? `Chat ${parts[1]}` : convId;
  };

  return (
    <div className="d-flex vh-100" style={{ backgroundColor: '#f8f9fa' }}>
      {/* Sidebar */}
      {showSidebar && (
        <div className="d-flex flex-column" style={{ width: '260px', backgroundColor: '#ffffff', borderRight: '1px solid #e5e5e5' }}>
          {/* New Chat Button */}
          <div className="p-3 border-bottom">
            <button 
              className="btn btn-primary w-100 d-flex align-items-center justify-content-center"
              onClick={createNewConversation}
            >
              <FaPlus className="me-2" />
              New Chat
            </button>
          </div>
           
          {/* Chat History */}
          <div className="flex-grow-1 p-3" style={{ overflowY: 'auto' }}>
            <div className="text-muted small mb-2">Recent Conversations</div>
            {conversations.slice().reverse().map((conv) => (
              <div 
                key={conv.id}
                className={`chat-item p-2 rounded hover-cursor d-flex justify-content-between align-items-center ${
                  currentConversationId === conv.id ? 'bg-light border-start border-3 border-primary' : ''
                }`}
                style={{ cursor: 'pointer' }}
                onClick={() => switchConversation(conv.id)}
              >
                <div className="small text-truncate flex-grow-1">
                  {formatConversationId(conv.id)}
                </div>
                <div className="d-flex align-items-center">
                  <span className="badge bg-secondary me-2" style={{ fontSize: '10px' }}>
                    {conv.message_count}
                  </span>
                  <button
                    className="btn btn-sm btn-link text-danger p-0"
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteConversation(conv.id);
                    }}
                  >
                    <FaTrash size={12} />
                  </button>
                </div>
              </div>
            ))}
            {conversations.length === 0 && (
              <div className="text-muted small text-center py-3">
                No conversations yet
              </div>
            )}
          </div>

          {/* Current Conversation Info */}
          {currentConversationId && (
            <div className="p-3 border-top bg-light">
              <div className="text-muted small">Current Chat</div>
              <div className="small text-truncate">{formatConversationId(currentConversationId)}</div>
              <div className="text-muted x-small">
                {chatHistory.filter(msg => msg.type === 'user').length} messages
              </div>
            </div>
          )}
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-grow-1 d-flex flex-column">
        {/* Header */}
        <div className="border-bottom bg-white p-3 d-flex justify-content-between align-items-center">
          <div className="d-flex align-items-center">
            <button 
              className="btn btn-outline-secondary border-0 me-2"
              onClick={() => setShowSidebar(!showSidebar)}
            >
              <FaHistory />
            </button>
            <span className="fw-bold fs-5" style={{ color: '#202123' }}>SineWise</span>
            {currentConversationId && (
              <span className="badge bg-light text-dark ms-2 small">
                {formatConversationId(currentConversationId)}
              </span>
            )}
          </div>
          <div className="d-flex align-items-center gap-3">
            <div className="dropdown">
              <button 
                className="btn btn-outline-secondary border-0 dropdown-toggle"
                onClick={() => setShowVideoDropdown(!showVideoDropdown)}
              >
                <FaVideo className="me-1" /> Videos
              </button>
              {showVideoDropdown && (
                <div className="dropdown-menu show">
                  <a className="dropdown-item" href="#" onClick={() => window.open(videoTopics.identities, '_blank')}>
                    Trigonometric Identities
                  </a>
                  <a className="dropdown-item" href="#" onClick={() => window.open(videoTopics.equations, '_blank')}>
                    Solving Equations
                  </a>
                  <a className="dropdown-item" href="#" onClick={() => window.open(videoTopics.fundamentals, '_blank')}>
                    Fundamentals
                  </a>
                </div>
              )}
            </div>
            <a href="/lesson" className="text-decoration-none text-dark">AI Tutor</a>
            <a href="/generate-lesson" className="text-decoration-none text-dark">Lesson</a>
            <a href="/graph" className="text-decoration-none text-dark">Graph</a>
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-grow-1 p-4" style={{ overflowY: 'auto', backgroundColor: '#ffffff' }}>
          {chatHistory.length === 0 ? (
            <div className="text-center text-muted mt-5">
              <div className="fs-4 mb-3">SineWise</div>
              <div className="fs-6">Your AI math solver and homework helper</div>
            </div>
          ) : (
            chatHistory.map((chat, index) => (
              <div key={index} className={`mb-6 ${chat.type === 'user' ? 'text-end' : ''}`}>
                <div className={`d-inline-block max-w-75 ${chat.type === 'user' ? 'text-start' : ''}`}>
                  <div className="fw-bold mb-1 small" style={{ color: '#6e6e80' }}>
                    {chat.type === 'user' ? 'You' : 'SineWise'}
                  </div>
                  <div 
                    className={`p-3 rounded ${
                      chat.type === 'user' 
                        ? 'bg-primary text-white' 
                        : 'bg-light border'
                    }`}
                    style={{ 
                      maxWidth: '100%',
                      wordWrap: 'break-word'
                    }}
                  >
                    {chat.type === 'user' ? (
                      chat.content
                    ) : (
                      <div>
                        {chat.content.error ? (
                          <div className="text-danger">{chat.content.error}</div>
                        ) : (
                          <>
                            <div className="mb-3">
                              <strong>✅ {chat.content.final_answer}</strong>
                            </div>
          
                            
                            {chat.content.solution_steps && chat.content.solution_steps.length > 0 && (
                              <div className="mt-3">
                                <button 
                                  className="btn btn-outline-primary btn-sm mb-2"
                                  onClick={() => toggleSteps(index)}
                                >
                                  {chat.showSteps ? (
                                    <>
                                      <FaEyeSlash className="me-1" />
                                      Hide steps
                                    </>
                                  ) : (
                                    <>
                                      <FaEye className="me-1" />
                                      Show steps
                                    </>
                                  )}
                                </button>
                                
                                {chat.showSteps && (
                                  <div className="border-start border-3 border-primary ps-3 bg-white rounded p-2">
                                    {chat.content.solution_steps.map((step, stepIndex) => (
                                      <div key={stepIndex} className="mb-2 small" style={{ lineHeight: '1.4' }}>
                                        {step.includes('**') ? (
                                          <div dangerouslySetInnerHTML={{ 
                                            __html: step.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                          }} />
                                        ) : (
                                          step
                                        )}
                                      </div>
                                    ))}
                                  </div>
                                )}
                              </div>
                            )}

                            {/* Graph Display */}
                            {chat.content.has_graph && chat.content.graph_image && (
                              <div className="mt-3">
                                <div className="fw-bold small mb-2">📈 Graph:</div>
                                <img 
                                  src={chat.content.graph_image} 
                                  alt="Graph" 
                                  className="img-fluid rounded border"
                                  style={{ maxWidth: '100%', height: 'auto' }}
                                />
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
          
          {loading && (
            <div className="text-center">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-top bg-white p-4">
          <div className="position-relative">
            <div className="input-group">
              <input 
                value={message} 
                onChange={e => setMessage(e.target.value)}
                className="form-control border-1 py-3 ps-4 pe-5"
                placeholder="Ask a trigonometry question... (try 'prove sin²θ + cos²θ = 1' or 'solve sin x = 0.5')"
                onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMsg()}
                disabled={loading}
                style={{ 
                  borderRadius: '12px',
                  borderColor: '#d1d5db',
                  fontSize: '16px'
                }}
              />
              <div className="position-absolute" style={{ right: '60px', top: '50%', transform: 'translateY(-50%)' }}>
                <button 
                  className="btn btn-link text-muted p-1 me-1"
                  onClick={() => setShowMathKeyboard(!showMathKeyboard)}
                  type="button"
                >
                  <FaCalculator size={18} />
                </button>
              </div>
              <button 
                className="btn position-absolute"
                onClick={sendMsg}
                disabled={loading || !message.trim()}
                style={{
                  right: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  backgroundColor: message.trim() ? '#10a37f' : '#cccccc',
                  border: 'none',
                  color: 'white',
                  borderRadius: '8px',
                  padding: '8px 12px',
                  transition: 'background-color 0.2s'
                }}
              >
                {loading ? (
                  <div className="spinner-border spinner-border-sm" />
                ) : (
                  <FaPaperPlane />
                )}
              </button>
            </div>
            
            {/* Math Keyboard */}
            {showMathKeyboard && (
              <div className="mt-3 p-3 border rounded bg-light">
                <div className="d-flex flex-wrap gap-1">
                  {mathSymbols.map((symbol, index) => (
                    <button
                      key={index}
                      className="btn btn-outline-secondary btn-sm px-2 py-1"
                      onClick={() => insertSymbol(symbol)}
                      type="button"
                      style={{ fontSize: '14px', minWidth: '40px' }}
                    >
                      {symbol}
                    </button>
                  ))}
                </div>
              </div>
            )}
            
            <div className="text-center text-muted small mt-2" style={{color:'red', fontWeight:'bold'}} >
              SineWise is an AI and may make mistake, please confirm the answers with a teacher!
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}