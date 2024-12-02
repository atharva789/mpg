import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api"; // Assuming api.js is configured for Axios requests
import "../styles/Home.css"; // Ensure CSS follows existing conventions

function Home() {
  const [assessments, setAssessments] = useState([]);
  const navigate = useNavigate();

  // Fetch assessments from the backend
  useEffect(() => {
    async function fetchAssessments() {
      try {
        const response = await api.get("/api/assessments/");
        setAssessments(response.data);
      } catch (error) {
        console.error("Error fetching assessments:", error);
      }
    }
    fetchAssessments();
  }, []);

  // Navigate to the Assessment page
  const handleAssessmentClick = (id) => {
    navigate(`/assessment/${id}`);
  };

  // Navigate to the Create Assessment page
  const handleCreateAssessment = () => {
    navigate("/create-assessment");
  };

  return (
    <div className="home-container">
      <h1>Assessments</h1>
      <button className="create-assessment-button" onClick={handleCreateAssessment}>
        Create Assessment
      </button>
      <ul className="assessments-list">
        {assessments.map((assessment) => (
          <li
            key={assessment.id}
            className="assessment-item"
            onClick={() => handleAssessmentClick(assessment.id)}
          >
            {assessment.title}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Home;