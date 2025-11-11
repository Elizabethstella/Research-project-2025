import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import { validateEnv } from "./config/env.js";

dotenv.config();

// Validate environment variables on startup
validateEnv();

const app = express();

// Middleware
app.use(cors());
app.use(express.json({ limit: "10mb" }));
app.use(express.urlencoded({ extended: true }));

// Import routes
import authRoutes from "./routes/auth.js";
import statsRoutes from "./routes/stats.js";
import apiGlueRoutes from "./routes/apiGlue.js";

// Health check endpoint
app.get("/api/health", (req, res) => {
  res.json({ 
    success: true,
    status: "Server is running", 
    timestamp: new Date().toISOString(),
    python_service: process.env.PYTHON_SERVICE_URL || "http://localhost:7000",
    environment: process.env.NODE_ENV || "development"
  });
});

// API Routes
app.use("/api/auth", authRoutes);
app.use("/api/stats", statsRoutes);
app.use("/api", apiGlueRoutes); // This includes all AI tutor routes

// 404 handler for undefined routes
app.use("/api/*", (req, res) => {
  res.status(404).json({
    success: false,
    error: "API endpoint not found"
  });
});

// Global error handling middleware
app.use((error, req, res, next) => {
  console.error("Global error handler:", error);
  res.status(500).json({
    success: false,
    error: "Internal server error"
  });
});

// Start server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || "development"}`);
  console.log(`Python service: ${process.env.PYTHON_SERVICE_URL || "http://localhost:7000"}`);
});

app.get('/api/debug-topics', (req, res) => {
  console.log("✅ Debug route hit!");
  res.json({ 
    success: true, 
    message: "Debug route works!",
    topics: ["test1", "test2"]
  });
});
export default app;