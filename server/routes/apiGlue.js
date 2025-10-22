import express from "express";
import axios from "axios";
import { auth } from "../middleware/auth.js";
import db from "../db.js";
import { recordAttempt } from "../services/analytics.js";

const router = express.Router();
const PYTHON_SERVICE_URL = process.env.PYTHON_SERVICE_URL || "http://localhost:7000";

// Helper function to detect if student disagrees
function studentDisagreed(msg) {
  const s = msg.toLowerCase();
  return ["wrong", "are you sure", "not right", "try again", "incorrect", "that's wrong"].some(p => s.includes(p));
}

// ------------------- AI TUTOR & SOLVER ROUTES ------------------- //

router.post("/solve", auth, async (req, res) => {
  try {
    const { question, topic = "Fundamentals" } = req.body;
    let q = question;
    
    // Handle student disagreement by fetching last question
    if (studentDisagreed(question)) {
      const last = db.prepare("SELECT question FROM attempts WHERE user_id=? ORDER BY id DESC LIMIT 1").get(req.user.id);
      if (last) q = last.question;
    }

    // Call Python service
    const pyRes = await axios.post(`${PYTHON_SERVICE_URL}/solve`, { question: q });
    const result = pyRes.data;
    
    // Record analytics
    recordAttempt(req.user.id, topic, result.confidence > 0.7, result.confidence || 0, q);
    
    // Return structured response for frontend
    res.json({
      success: true,
      solution: result.solution || [],
      confidence: result.confidence || 0,
      method: result.method || "",
      source: result.source || "",
      matched_question: result.matched_question || "",
      category: result.category || "",
      has_graph: result.has_graph || false,
      graph_image: result.graph_image || null
    });
    
  } catch (e) {
    console.error("Solve error:", e);
    res.status(500).json({ error: "AI Tutor failed to solve the problem" });
  }
});

router.post("/tutor-help", auth, async (req, res) => {
  try {
    const { problem, context = "" } = req.body;
    
    const pyRes = await axios.post(`${PYTHON_SERVICE_URL}/tutor-help`, {
      problem,
      context
    });
    
    const result = pyRes.data;
    
    // Record tutor help request
    recordAttempt(req.user.id, "tutor_help", true, 0, problem);
    
    res.json({
      success: true,
      tutor_response: result.tutor_response,
      solution_steps: result.solution_steps || [],
      hints: result.hints || [],
      confidence: result.confidence || 0,
      has_graph: result.has_graph || false,
      graph_image: result.graph_image || null
    });
    
  } catch (e) {
    console.error("Tutor help error:", e);
    res.status(500).json({ error: "Failed to get tutor help" });
  }
});

// ------------------- LESSON ROUTES ------------------- //

router.post("/generate-lesson", auth, async (req, res) => {
  try {
    const { topic } = req.body;
    
    const pyRes = await axios.post(`${PYTHON_SERVICE_URL}/generate_lesson`, { topic });
    const result = pyRes.data;
    
    // Record lesson generation
    recordAttempt(req.user.id, "lesson_generation", true, 0, `Lesson: ${topic}`);
    
    res.json(result);
    
  } catch (e) {
    console.error("Lesson generation error:", e);
    res.status(500).json({ error: "Failed to generate lesson" });
  }
});

router.get("/lesson-topics", auth, async (req, res) => {
  try {
    const pyRes = await axios.get(`${PYTHON_SERVICE_URL}/lesson_topics`);
    res.json(pyRes.data);
  } catch (e) {
    console.error("Lesson topics error:", e);
    res.status(500).json({ error: "Failed to get lesson topics" });
  }
});

router.get("/lesson-stats", auth, async (req, res) => {
  try {
    const pyRes = await axios.get(`${PYTHON_SERVICE_URL}/lesson_stats`);
    res.json(pyRes.data);
  } catch (e) {
    console.error("Lesson stats error:", e);
    res.status(500).json({ error: "Failed to get lesson stats" });
  }
});

// ------------------- QUIZ ROUTES ------------------- //

router.post("/generate-quiz", auth, async (req, res) => {
  try {
    const { topic, num_questions = 5 } = req.body;
    
    const pyRes = await axios.post(`${PYTHON_SERVICE_URL}/generate_quiz`, {
      topic,
      num_questions
    });
    
    const result = pyRes.data;
    
    // Record quiz generation
    recordAttempt(req.user.id, "quiz_generation", true, 0, `Quiz: ${topic}`);
    
    res.json(result);
    
  } catch (e) {
    console.error("Quiz generation error:", e);
    res.status(500).json({ error: "Failed to generate quiz" });
  }
});

router.post("/quiz-question-answer", auth, async (req, res) => {
  try {
    const { quiz_id, question_id } = req.body;
    
    const pyRes = await axios.post(`${PYTHON_SERVICE_URL}/quiz_question_answer`, {
      quiz_id,
      question_id
    });
    
    res.json(pyRes.data);
    
  } catch (e) {
    console.error("Quiz answer error:", e);
    res.status(500).json({ error: "Failed to get question answer" });
  }
});

router.post("/quiz-progress", auth, async (req, res) => {
  try {
    const { quiz_id } = req.body;
    
    const pyRes = await axios.post(`${PYTHON_SERVICE_URL}/quiz_progress`, {
      quiz_id
    });
    
    res.json(pyRes.data);
    
  } catch (e) {
    console.error("Quiz progress error:", e);
    res.status(500).json({ error: "Failed to get quiz progress" });
  }
});

router.get("/quiz-topics", auth, async (req, res) => {
  try {
    const pyRes = await axios.get(`${PYTHON_SERVICE_URL}/quiz_topics`);
    res.json(pyRes.data);
  } catch (e) {
    console.error("Quiz topics error:", e);
    res.status(500).json({ error: "Failed to get quiz topics" });
  }
});

router.get("/popular-quiz-topics", auth, async (req, res) => {
  try {
    const pyRes = await axios.get(`${PYTHON_SERVICE_URL}/popular_quiz_topics`);
    res.json(pyRes.data);
  } catch (e) {
    console.error("Popular quiz topics error:", e);
    res.status(500).json({ error: "Failed to get popular quiz topics" });
  }
});

router.get("/quiz-stats", auth, async (req, res) => {
  try {
    const pyRes = await axios.get(`${PYTHON_SERVICE_URL}/quiz_stats`);
    res.json(pyRes.data);
  } catch (e) {
    console.error("Quiz stats error:", e);
    res.status(500).json({ error: "Failed to get quiz stats" });
  }
});

// ------------------- GRAPH ROUTES ------------------- //

router.post("/generate-graph", auth, async (req, res) => {
  try {
    const { expression, question } = req.body;
    
    const pyRes = await axios.post(`${PYTHON_SERVICE_URL}/graph`, {
      expression,
      question
    });
    
    const result = pyRes.data;
    
    // Record graph generation
    recordAttempt(req.user.id, "graph_generation", true, 0, `Graph: ${expression}`);
    
    res.json(result);
    
  } catch (e) {
    console.error("Graph generation error:", e);
    res.status(500).json({ error: "Failed to generate graph" });
  }
});

// ------------------- OCR ROUTES ------------------- //

router.post("/process-image", auth, async (req, res) => {
  try {
    // Note: File uploads need special handling
    // This is a simplified version - you might need multer for file handling
    
    const pyRes = await axios.post(`${PYTHON_SERVICE_URL}/process-image`, req.body, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    res.json(pyRes.data);
    
  } catch (e) {
    console.error("OCR processing error:", e);
    res.status(500).json({ error: "Failed to process image" });
  }
});

// ------------------- USER PROFILE ROUTES ------------------- //

router.get("/user/me", auth, async (req, res) => {
  try {
    const user = db.prepare("SELECT id, name, email, role FROM users WHERE id = ?").get(req.user.id);
    if (!user) {
      return res.status(404).json({ error: "User not found" });
    }
    res.json(user);
  } catch (e) {
    console.error("User profile error:", e);
    res.status(500).json({ error: "Failed to get user profile" });
  }
});

export default router;