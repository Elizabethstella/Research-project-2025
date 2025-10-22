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
};

// AI Tutor endpoints
export const tutorAPI = {
  solveProblem: (question, topic = "Fundamentals") => 
    api.post('/solve', { question, topic }),
  
  getTutorHelp: (problem, context = "") => 
    api.post('/tutor-help', { problem, context }),
};

// Lesson endpoints
export const lessonAPI = {
  generateLesson: (topic) => 
    api.post('/generate-lesson', { topic }),
  
  getLessonTopics: () => 
    api.get('/lesson-topics'),
  
  getLessonStats: () => 
    api.get('/lesson-stats'),
};

// Quiz endpoints
export const quizAPI = {
  generateQuiz: (topic, num_questions = 5) => 
    api.post('/generate-quiz', { topic, num_questions }),
  
  getQuestionAnswer: (quiz_id, question_id) => 
    api.post('/quiz-question-answer', { quiz_id, question_id }),
  
  getQuizProgress: (quiz_id) => 
    api.post('/quiz-progress', { quiz_id }),
  
  getQuizTopics: () => 
    api.get('/quiz-topics'),
  
  getPopularQuizTopics: () => 
    api.get('/popular-quiz-topics'),
  
  getQuizStats: () => 
    api.get('/quiz-stats'),
};

// Graph endpoints
export const graphAPI = {
  generateGraph: (expression, question = "") => 
    api.post('/generate-graph', { expression, question }),
};

// OCR endpoints
export const ocrAPI = {
  processImage: (imageFile) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    return api.post('/process-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
};

// Health check
export const healthCheck = () => api.get('/health');