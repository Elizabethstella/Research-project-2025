import express from "express";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import rateLimit from "express-rate-limit";
import db from "../db.js";
import dotenv from "dotenv";
import { validateLogin, validateRegister } from "../middleware/validation.js";
import { checkDB } from "../middleware/dbHealth.js";

dotenv.config();

const router = express.Router();

// Rate limiting
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // limit each IP to 5 requests per windowMs
  message: { 
    success: false,
    error: "Too many authentication attempts, please try again later" 
  }
});

router.post("/register", authLimiter, checkDB, validateRegister, async (req, res) => {
  const { name, email, password } = req.body;
  
  try {
    const hash = await bcrypt.hash(password, 10);
   const result = await db.prepare("INSERT INTO users(name, email, password, role) VALUES (?, ?, ?, 'student')").run(name, email, hash);
    
    // Create user stats entry
    db.prepare(`
      INSERT INTO user_stats (user_id, total_prompts, correct_answers, wrong_answers, total_time_seconds) 
      VALUES (?, 0, 0, 0, 0)
    `).run(result.lastInsertRowid);
    
    res.json({ 
      success: true, 
      message: "Registered successfully" 
    });
  } catch (error) {
    if (error.code === 'SQLITE_CONSTRAINT_UNIQUE') {
      res.status(400).json({ 
        success: false,
        error: "Email already exists" 
      });
    } else {
      console.error("Registration error:", error);
      res.status(500).json({ 
        success: false,
        error: "Registration failed" 
      });
    }
  }
});

router.post("/login", authLimiter, checkDB, validateLogin, async (req, res) => {
  const { email, password } = req.body;
  
  try {
   const u = await db.prepare("SELECT * FROM users WHERE email = ?").get(email);
    if (!u) {
      return res.status(400).json({ 
        success: false,
        error: "Invalid credentials" 
      });
    }
    
    const passwordMatch = await bcrypt.compare(password, u.password);
    if (!passwordMatch) {
      return res.status(400).json({ 
        success: false,
        error: "Invalid credentials" 
      });
    }
    
    const token = jwt.sign(
      { 
        id: u.id, 
        role: u.role,
        email: u.email 
      }, 
      process.env.JWT_SECRET,
      { expiresIn: '7d' }
    );
    
    res.json({ 
      success: true,
      token,
      user: {
        id: u.id,
        name: u.name,
        email: u.email,
        role: u.role
      }
    });
    
  } catch (error) {
    console.error("Login error:", error);
    res.status(500).json({ 
      success: false,
      error: "Login failed" 
    });
  }
});

export default router;