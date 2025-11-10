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
    const { question, topic = "Fundamentals", conversation_id } = req.body;
    let q = question;
    
    // Handle student disagreement by fetching last question
    if (studentDisagreed(question)) {
      const last = db.prepare("SELECT question FROM attempts WHERE user_id=? ORDER BY id DESC LIMIT 1").get(req.user.id);
      if (last) q = last.question;
    }

    // Call Python service with conversation_id
    const pyRes = await axios.post(`${PYTHON_SERVICE_URL}/solve`, { 
      question: q, 
      conversation_id 
    });
    const result = pyRes.data;
    
    // Record analytics
    recordAttempt(req.user.id, topic, result.confidence > 0.7, result.confidence || 0, q);
    
    // Return enhanced response with conversation support
    res.json({
      success: true,
      final_answer: result.final_answer || "No solution available",
      solution_steps: result.solution_steps || [],
      has_graph: result.has_graph || false,
      graph_image: result.graph_image || null,
      conversation_id: result.conversation_id || conversation_id, // Return conversation ID
      available_alternative: result.available_alternative || false,
      has_follow_up: result.has_follow_up || false
    });
    
  } catch (e) {
    console.error("Solve error:", e);
    res.status(500).json({ 
      success: false,
      error: "AI Tutor failed to solve the problem",
      final_answer: "Sorry, I couldn't solve this problem. Please try again.",
      solution_steps: []
    });
  }
});




router.get("/conversations", auth, async (req, res) => {
  try {
    const pyRes = await axios.get(`${PYTHON_SERVICE_URL}/conversations`);
    res.json(pyRes.data);
  } catch (e) {
    console.error("Get conversations error:", e);
    res.status(500).json({ 
      success: false,
      error: "Failed to get conversations" 
    });
  }
});

router.get("/conversations/:conversationId", auth, async (req, res) => {
  try {
    const { conversationId } = req.params;
    const pyRes = await axios.get(`${PYTHON_SERVICE_URL}/conversations/${conversationId}`);
    res.json(pyRes.data);
  } catch (e) {
    console.error("Get conversation error:", e);
    res.status(500).json({ 
      success: false,
      error: "Failed to get conversation" 
    });
  }
});

router.delete("/conversations/:conversationId", auth, async (req, res) => {
  try {
    const { conversationId } = req.params;
    const pyRes = await axios.delete(`${PYTHON_SERVICE_URL}/conversations/${conversationId}`);
    res.json(pyRes.data);
  } catch (e) {
    console.error("Delete conversation error:", e);
    res.status(500).json({ 
      success: false,
      error: "Failed to delete conversation" 
    });
  }
});

// -------------------  LESSON ROUTES ------------------- //

router.post("/generate_lesson", auth, async (req, res) => {
  try {
    const { topic, student_id, section_index = 0 } = req.body;
    
    if (!topic) {
      return res.status(400).json({ error: "Topic is required" });
    }

    const pyRes = await axios.post(`${PYTHON_SERVICE_URL}/generate_lesson`, {
      topic,
      student_id: student_id || req.user.id,
      section_index
    });
    
    const result = pyRes.data;
    
    // Record lesson generation
    recordAttempt(req.user.id, "lesson_generation", true, 0, `Lesson: ${topic}`);
    
    res.json(result);
    
  } catch (e) {
    console.error("Lesson generation error:", e);
    res.status(500).json({ 
      success: false,
      error: "Failed to generate lesson",
      details: e.message 
    });
  }
});
// NEW: Multi-topic lesson management
router.post("/lessons/start-topic", auth, async (req, res) => {
  try {
    const { topic_id } = req.body;
    const user_id = req.user.id;
    
    const pyRes = await axios.post(`${PYTHON_SERVICE_URL}/lessons/start-topic`, {
      student_id: user_id,
      topic_id
    });
    
    // Record topic start
    recordAttempt(user_id, "topic_started", true, 0, `Started topic: ${topic_id}`);
    
    res.json(pyRes.data);
    
  } catch (e) {
    console.error("Start topic error:", e);
    res.status(500).json({ 
      success: false,
      error: "Failed to start topic"
    });
  }
});

router.post("/lessons/continue-topic", auth, async (req, res) => {
  try {
    const { topic_id, student_id } = req.body; // Use same parameter names as client
    
    console.log("Continue topic request:", { student_id, topic_id });
    
    const pyRes = await axios.post(`${PYTHON_SERVICE_URL}/lessons/continue-topic`, {
      student_id: student_id || req.user.id, // Fallback to authenticated user
      topic_id
    });
    
    console.log("Continue topic response:", pyRes.data);
    
    res.json(pyRes.data);
    
  } catch (e) {
    console.error("Continue topic error:", e.message);
    
    // More detailed error response
    res.status(500).json({ 
      success: false,
      error: "Failed to continue topic",
      details: e.message,
      python_service_url: PYTHON_SERVICE_URL
    });
  }
});



router.get("/lesson_topics", auth, async (req, res) => {
  try {
    const pyRes = await axios.get(`${PYTHON_SERVICE_URL}/lesson_topics`);
    res.json(pyRes.data);
  } catch (e) {
    console.error("Lesson topics error:", e);
    res.status(500).json({ error: "Failed to get lesson topics" });
  }
});







// ------------------- GRAPH ROUTES ------------------- //

router.post("/graph", auth, async (req, res) => {
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

// Missing lesson routes
router.post("/lessons/section", auth, async (req, res) => {
  try {
    const { student_id, topic_id, section_index } = req.body;
    
    const pyRes = await axios.post(`${PYTHON_SERVICE_URL}/lessons/section`, {
      student_id,
      topic_id, 
      section_index
    });
    
    res.json(pyRes.data);
    
  } catch (e) {
    console.error("Lesson section error:", e);
    res.status(500).json({ error: "Failed to get lesson section" });
  }
});

router.post("/lessons/ask", auth, async (req, res) => {
  try {
    const { topic_id, question, conversation, student_id } = req.body;
    
    const pyRes = await axios.post(`${PYTHON_SERVICE_URL}/lessons/ask`, {
      topic_id,
      question,
      conversation,
      student_id: student_id || req.user.id
    });
    
    res.json(pyRes.data);
    
  } catch (e) {
    console.error("Ask question error:", e);
    res.status(500).json({ error: "Failed to ask question" });
  }
});




export default router;