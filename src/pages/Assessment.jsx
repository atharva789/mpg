import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../api"; // Axios API configured
import "../styles/Assessment.css";

function Assessment() {
  const { id } = useParams(); // Get the assessment ID from the URL
  const navigate = useNavigate();
  const [assessment, setAssessment] = useState(null);
  const [resources, setResources] = useState([]);
  const [packetUrl, setPacketUrl] = useState(null);

  // Fetch assessment details and associated data
  useEffect(() => {
    async function fetchAssessmentData() {
      try {
        const assessmentResponse = await api.get(`/api/assessments/${id}/`);
        setAssessment(assessmentResponse.data);

      } catch (error) {
        console.error("Error fetching assessment: Assessment data:", error);
      }
      try {
        const resourcesResponse = await api.get(`/api/resources/${id}/`); //
        setResources(resourcesResponse.data);

      } catch(error) {
        console.error("Error fetching assessment: Resource data:", error);
      }
      try {
        const packetResponse = await api.get(`/api/packets/${id}/`);
        setPacketUrl(packetResponse.data.pdf_file);
      } catch(error) {
          if (error.packetResponse && error.packetResponse.status === 404) {
            //generate packet
            packetResponse = await api.post(`/api/assessments/${id}/generate-packet/`)
          } else {
            // Handle other types of errors
                console.error("Error fetching assessment: Packet data:", error);
          }
      }
    }
    fetchAssessmentData();
  }, [id]);

  return (
    <div className="assessment-container">
      <div className="header">
        <h1>{assessment?.title}</h1>
        <button className="home-button" onClick={() => navigate("/")}>
          Home
        </button>
      </div>
      <div className="content">
        <div className="resources-sidebar">
          <h2>Resources</h2>
          <ul>
            {resources.map((resource) => (
              <li key={resource.id}>{resource.title}</li>
            ))}
          </ul>
        </div>
        <div className="packet-viewer">
          <h2>Exam Packet</h2>
          {packetUrl ? (
            <iframe
              src={packetUrl}
              title="Exam Packet"
              className="pdf-viewer"
            ></iframe>
          ) : (
            <p>No packet generated yet.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default Assessment;