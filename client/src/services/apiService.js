import api from '../api';

// Auth endpoints
export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (name, email, password) => api.post('/auth/register', { name, email, password }),
};

// User endpoints
export const userAPI = {
  getCurrentUser: () => api.get('/user/me'),
  getUserStats: () => api.get('/user/stats'),
  getUserProgress: () => api.get('/user/progress'),
  updateProfile: (profileData) => api.put('/user/profile', profileData),
  getLearningStats: () => api.get('/user/learning-stats'),
};

// Enhanced Lesson endpoints - FIXED AND CONSISTENT
export const lessonAPI = {
  // Legacy endpoints (for compatibility)
  generateLesson: (topic, studentId = null, sectionIndex = 0) => 
    api.post('/generate_lesson', { 
      topic, 
      student_id: studentId, 
      section_index: sectionIndex 
    }),
  getLessonTopics: () => api.get('/lesson_topics'),
  getLessonStats: () => api.get('/lesson_stats'),

 
  getTopics: () => api.get('/lessons/topics'), // CHANGED from getAvailableTopics
  
  startTopic: (studentId, topicId) => 
    api.post('/lessons/start-topic', { student_id: studentId, topic_id: topicId }),
  
  continueTopic: (studentId, topicId) => 
    api.post('/lessons/continue-topic', { student_id: studentId, topic_id: topicId }),
  
  // FIXED: Consistent naming
  getLessonSection: (studentId, topicId, sectionIndex) => // CHANGED from getSection
    api.post('/lessons/section', { 
      student_id: studentId, 
      topic_id: topicId, 
      section_index: sectionIndex 
    }),
  
  askQuestion: (topicId, question, conversation = [], studentId) => 
    api.post('/lessons/ask', { 
      topic_id: topicId, 
      question, 
      conversation, 
      student_id: studentId 
    }),

  // Pre-test and Post-test endpoints
};

// Student progress endpoints - FIXED (remove duplicate getProgress)
export const studentAPI = {
  getProgress: (studentId) => api.get(`/students/${studentId}/progress`),
  getDashboard: (studentId) => api.get(`/students/${studentId}/dashboard`),
  updateProgress: (studentId, progressData) => 
    api.put(`/students/${studentId}/progress`, progressData),
  
  // Alternative if PUT doesn't work
  updateProgressPost: (studentId, progressData) => 
    api.post(`/students/${studentId}/progress/update`, progressData),
  
  markTopicCompleted: (studentId, topicId, score) =>
    api.post(`/students/${studentId}/topics/${topicId}/complete`, { score }),
};

// AI Tutor endpoints
export const tutorAPI = {
  solveProblem: (question, topic = "Fundamentals", conversationId = null) => 
    api.post('/solve', { question, topic, conversation_id: conversationId }),
  
  getTutorHelp: (problem, context = "", conversationId = null) => 
    api.post('/tutor-help', { problem, context, conversation_id: conversationId }),
};

export const conversationAPI = {
  createConversation: () => api.post('/conversations/new'),
  getConversations: () => api.get('/conversations'),
  getConversation: (conversationId) => api.get(`/conversations/${conversationId}`),
  deleteConversation: (conversationId) => api.delete(`/conversations/${conversationId}`),
  solveWithConversation: (question, conversationId) => 
    api.post('/solve', { question, conversation_id: conversationId }),
};



