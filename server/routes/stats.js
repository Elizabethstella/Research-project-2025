import express from "express";
import { auth } from "../middleware/auth.js";
import { 
  getUserStats, 
  getAllUsersStats, 
  getUserProgress,
  getUserTopicStats,
  getLeaderboard,
  getWeeklyActivity
} from "../services/analytics.js";

const router = express.Router();

// Get current user's stats
router.get("/user/stats", auth, (req, res) => {
  try {
    const stats = getUserStats(req.user.id);
    if (!stats) {
      return res.status(404).json({ error: "User stats not found" });
    }
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error("Stats error:", error);
    res.status(500).json({ 
      success: false,
      error: "Failed to get user stats" 
    });
  }
});

// Get user progress over time
router.get("/user/progress", auth, (req, res) => {
  try {
    const days = parseInt(req.query.days) || 30;
    const progress = getUserProgress(req.user.id, days);
    res.json({
      success: true,
      data: progress
    });
  } catch (error) {
    console.error("Progress error:", error);
    res.status(500).json({ 
      success: false,
      error: "Failed to get user progress" 
    });
  }
});

// Get user topic performance breakdown
router.get("/user/topics", auth, (req, res) => {
  try {
    const topicStats = getUserTopicStats(req.user.id);
    res.json({
      success: true,
      data: topicStats
    });
  } catch (error) {
    console.error("Topic stats error:", error);
    res.status(500).json({ 
      success: false,
      error: "Failed to get topic stats" 
    });
  }
});

// Get weekly activity
router.get("/user/weekly-activity", auth, (req, res) => {
  try {
    const weeklyActivity = getWeeklyActivity(req.user.id);
    res.json({
      success: true,
      data: weeklyActivity
    });
  } catch (error) {
    console.error("Weekly activity error:", error);
    res.status(500).json({ 
      success: false,
      error: "Failed to get weekly activity" 
    });
  }
});

// Get leaderboard
router.get("/leaderboard", auth, (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 10;
    const leaderboard = getLeaderboard(limit);
    res.json({
      success: true,
      data: leaderboard
    });
  } catch (error) {
    console.error("Leaderboard error:", error);
    res.status(500).json({ 
      success: false,
      error: "Failed to get leaderboard" 
    });
  }
});

// Admin only - get all users stats
router.get("/admin/users", auth, (req, res) => {
  if (req.user.role !== "admin") {
    return res.status(403).json({ 
      success: false,
      error: "Admin access required" 
    });
  }
  try {
    const stats = getAllUsersStats();
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error("Admin stats error:", error);
    res.status(500).json({ 
      success: false,
      error: "Failed to get admin stats" 
    });
  }
});

export default router;