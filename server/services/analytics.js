import db from "../db.js";

export function recordAttempt(userId, topic, correct, timeSeconds = 0, question = "") {
  try {
    // Input validation
    if (!userId || typeof userId !== 'number') {
      throw new Error("Invalid user ID");
    }
    
    if (!topic || typeof topic !== 'string') {
      throw new Error("Topic must be a non-empty string");
    }
    
    if (typeof correct !== 'boolean') {
      throw new Error("Correct must be a boolean");
    }
    
    if (timeSeconds < 0) {
      throw new Error("Time seconds cannot be negative");
    }

    // Insert attempt record
    db.prepare(
      "INSERT INTO attempts (user_id, topic, correct, time_seconds, question) VALUES (?,?,?,?,?)"
    ).run(userId, topic, correct ? 1 : 0, timeSeconds, question);

    // Update user stats
    const user = db.prepare("SELECT * FROM users WHERE id=?").get(userId);
    if (!user) {
      console.warn(`User ${userId} not found when recording attempt`);
      return false;
    }
    
    const newCorrect = user.correct_answers + (correct ? 1 : 0);
    const newWrong = user.wrong_answers + (!correct ? 1 : 0);
    const newPrompts = user.total_prompts + 1;
    const newTime = user.total_time_seconds + timeSeconds;

    db.prepare(
      "UPDATE users SET correct_answers=?, wrong_answers=?, total_prompts=?, total_time_seconds=?, most_topic=? WHERE id=?"
    ).run(newCorrect, newWrong, newPrompts, newTime, topic, userId);
    
    return true;
  } catch (error) {
    console.error("Error recording attempt:", error);
    return false;
  }
}

// Batch operations for better performance
export function recordAttemptsBatch(attempts) {
  const insertAttempt = db.prepare(
    "INSERT INTO attempts (user_id, topic, correct, time_seconds, question) VALUES (?,?,?,?,?)"
  );
  
  const updateUser = db.prepare(`
    UPDATE users 
    SET correct_answers = correct_answers + ?, 
        wrong_answers = wrong_answers + ?,
        total_prompts = total_prompts + 1,
        total_time_seconds = total_time_seconds + ?,
        most_topic = ?
    WHERE id = ?
  `);
  
  const transaction = db.transaction((attempts) => {
    for (const attempt of attempts) {
      const { userId, topic, correct, timeSeconds = 0, question = "" } = attempt;
      
      insertAttempt.run(userId, topic, correct ? 1 : 0, timeSeconds, question);
      updateUser.run(
        correct ? 1 : 0,
        correct ? 0 : 1,
        timeSeconds,
        topic,
        userId
      );
    }
  });
  
  try {
    transaction(attempts);
    return true;
  } catch (error) {
    console.error("Error recording batch attempts:", error);
    return false;
  }
}

export const getUserStats = (userId) => {
  try {
    const user = db.prepare("SELECT * FROM users WHERE id=?").get(userId);
    if (!user) return null;
    
    // Calculate additional stats
    const totalAttempts = user.correct_answers + user.wrong_answers;
    const accuracy = totalAttempts > 0 ? (user.correct_answers / totalAttempts) * 100 : 0;
    const avgTime = totalAttempts > 0 ? user.total_time_seconds / totalAttempts : 0;
    
    return {
      ...user,
      accuracy: Math.round(accuracy * 100) / 100, // Round to 2 decimal places
      avgTimePerQuestion: Math.round(avgTime * 100) / 100,
      totalAttempts
    };
  } catch (error) {
    console.error("Error getting user stats:", error);
    return null;
  }
};

export const getAllUsersStats = () => {
  try {
    const users = db.prepare(
      `SELECT 
        id, name, email, 
        total_prompts, 
        correct_answers, 
        wrong_answers, 
        total_time_seconds, 
        most_topic 
       FROM users 
       ORDER BY total_prompts DESC`
    ).all();
    
    return users.map(user => ({
      ...user,
      accuracy: user.total_prompts > 0 
        ? Math.round((user.correct_answers / user.total_prompts) * 10000) / 100 
        : 0,
      avgTimePerQuestion: user.total_prompts > 0 
        ? Math.round((user.total_time_seconds / user.total_prompts) * 100) / 100 
        : 0
    }));
  } catch (error) {
    console.error("Error getting all users stats:", error);
    return [];
  }
};

// Get user progress over time
export function getUserProgress(userId, days = 30) {
  try {
    return db.prepare(`
      SELECT 
        DATE(timestamp) as date,
        COUNT(*) as total_attempts,
        SUM(correct) as correct_attempts,
        AVG(time_seconds) as avg_time
      FROM attempts 
      WHERE user_id = ? AND timestamp >= DATE('now', '-' || ? || ' days')
      GROUP BY DATE(timestamp)
      ORDER BY date DESC
    `).all(userId, days);
  } catch (error) {
    console.error("Error getting user progress:", error);
    return [];
  }
}

// Get topic performance breakdown
export function getUserTopicStats(userId) {
  try {
    return db.prepare(`
      SELECT 
        topic,
        COUNT(*) as total_attempts,
        SUM(correct) as correct_attempts,
        AVG(time_seconds) as avg_time,
        (SUM(correct) * 1.0 / COUNT(*)) * 100 as success_rate
      FROM attempts 
      WHERE user_id = ?
      GROUP BY topic
      ORDER BY total_attempts DESC
    `).all(userId);
  } catch (error) {
    console.error("Error getting user topic stats:", error);
    return [];
  }
}

// Get leaderboard
export function getLeaderboard(limit = 10) {
  try {
    return db.prepare(`
      SELECT 
        id, name, email,
        total_prompts,
        correct_answers,
        wrong_answers,
        (correct_answers * 1.0 / total_prompts) * 100 as accuracy,
        total_time_seconds
      FROM users 
      WHERE total_prompts > 0
      ORDER BY accuracy DESC, total_prompts DESC
      LIMIT ?
    `).all(limit);
  } catch (error) {
    console.error("Error getting leaderboard:", error);
    return [];
  }
}

// Get weekly activity
export function getWeeklyActivity(userId) {
  try {
    return db.prepare(`
      SELECT 
        strftime('%W', timestamp) as week_number,
        COUNT(*) as total_attempts,
        SUM(correct) as correct_attempts,
        AVG(time_seconds) as avg_time
      FROM attempts 
      WHERE user_id = ? AND timestamp >= DATE('now', '-12 weeks')
      GROUP BY week_number
      ORDER BY week_number DESC
    `).all(userId);
  } catch (error) {
    console.error("Error getting weekly activity:", error);
    return [];
  }
}