import React, { useEffect, useState } from "react";
import api from "../api";

export default function AdminDashboard() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    async function fetchUsers() {
      const res = await api.get("/admin/users");
      setUsers(res.data);
    }
    fetchUsers();
  }, []);

  return (
    <div className="container mt-5">
      <h2 className="text-center text-primary mb-4">Admin Dashboard</h2>
      <table className="table table-bordered table-striped">
        <thead className="table-light">
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Prompts</th>
            <th>Correct</th>
            <th>Wrong</th>
            <th>Most Active Topic</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u, i) => (
            <tr key={i}>
              <td>{u.name}</td>
              <td>{u.email}</td>
              <td>{u.stats?.totalPrompts || 0}</td>
              <td>{u.stats?.correctAnswers || 0}</td>
              <td>{u.stats?.wrongAnswers || 0}</td>
              <td>{u.stats?.mostTopic || "N/A"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
