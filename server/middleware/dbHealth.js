import db from "../db.js";

export function checkDB(req, res, next) {
  try {
    // Simple query to check DB connection
    db.prepare("SELECT 1").get();
    next();
  } catch (error) {
    console.error("Database health check failed:", error);
    res.status(503).json({ 
      success: false,
      error: "Service temporarily unavailable" 
    });
  }
}