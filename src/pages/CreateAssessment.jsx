import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import "../styles/CreateAssessment.css";

function CreateAssessment() {
  const [title, setTitle] = useState("");
  const [assessmentType, setAssessmentType] = useState("");
  const [dueDate, setDueDate] = useState(""); // Store due date
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
  e.preventDefault();
  try {
    const response = await api.post("/api/assessments/", {
      title,
      assessment_type: assessmentType,
      due_date: dueDate,
    });
    console.log(response.data.id); // Should now correctly log the assessmentId
    navigate(`/upload-resources/${response.data.id}`);
  } catch (error) {
    console.error("Error creating assessment:", error.response?.data || error.message);
  }
};

  return (
    <div className="create-assessment-container">
      <h1>Create Assessment</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Title:
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </label>
        <label>
          Type:
          <input
            type="text"
            value={assessmentType}
            onChange={(e) => setAssessmentType(e.target.value)}
            required
          />
        </label>
        <label>
          Due Date:
          {/* Date-Time Picker Input */}
          <input
            type="datetime-local"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            required
          />
        </label>
        <button type="submit">Create Assessment</button>
      </form>
    </div>
  );
}

export default CreateAssessment;