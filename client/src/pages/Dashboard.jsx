import React, { useEffect, useState } from 'react';
import { userAPI } from "../services/apiService";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [user, setUser] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const u = await userAPI.getCurrentUser();
        setUser(u.data);
        const s = await userAPI.getUserStats();
        setStats(s.data);
      } catch (err) { 
        console.error("Dashboard error:", err); 
      }
    }
    load();
  }, []);

  // ... rest of your Dashboard.jsx component

  // ... rest of the component remains the same

  if (!user || !stats) return <div className="container py-4">Loading...</div>;

  const minutes = Math.round((stats.totalTimeSeconds||0)/60);
  const mostTopic = Object.entries(stats.topicPromptCount||{Fundamentals:0,Identities:0,Equations:0}).sort((a,b)=>b[1]-a[1])[0][0];

  return (
    <div className="container py-4">
      <h3>Welcome, {user.name}</h3>
      <div className="row g-3 mt-3">
        <div className="col-md-4"><div className="card p-3"><h5>{stats.totalPrompts}</h5><small>Total prompts</small></div></div>
        <div className="col-md-4"><div className="card p-3"><h5>{stats.correctAnswers}</h5><small>Correct</small></div></div>
        <div className="col-md-4"><div className="card p-3"><h5>{stats.wrongAnswers}</h5><small>Wrong</small></div></div>
      </div>

      <div className="card mt-3 p-3">
        <h5>Topic counts</h5>
        <ul>
          {Object.entries(stats.topicPromptCount||{}).map(([t,c])=> <li key={t}>{t}: {c}</li>)}
        </ul>
      </div>

      <div className="mt-3">
        <p><strong>Time spent:</strong> {minutes} minutes</p>
        <p><strong>Most prompted topic:</strong> {mostTopic}</p>
      </div>
    </div>
  );
}
