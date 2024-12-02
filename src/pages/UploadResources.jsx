import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../api";
import "../styles/UploadResources.css";
import LoadingIndicator from "../components/LoadingIndicator";


function UploadResources() {
  const { assessmentId } = useParams();
  const [syllabus, setSyllabus] = useState(null);
  const [resourceFiles, setResourceFiles] = useState([]);

  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!assessmentId) {
      setMessage("Assessment ID is missing.");
      return;
    }
    if (assessmentId) {console.log(assessmentId + " assessment being referred to")
    }

    const formData = new FormData();
    formData.append("syllabus", syllabus); // Attach syllabus file
    resourceFiles.forEach((file, index) => {
      formData.append(`resources_${index}`, file); // Attach resource files
    });

    try {
// UploadResources.jsx
      const response = await api.post(`/api/resources/${assessmentId}/upload/`, formData);      
      setMessage("Resources uploaded successfully.");
      //create assessment when resource uploaded
    } catch (error) {
      console.error("Error uploading resources:", error.response?.data || error.message);
      setMessage("Error uploading resources.");
    }
    setLoading(true);
    try {
      const Packetresponse = await api.post(`/api/assessments/${assessmentId}/generate-packet/`);
      navigate(`/assessment/${assessmentId}`);
    } catch (error) {
      console.error("Error uploading resources:Packet Generate:", error.Packetresponse?.data || error.message);
      setMessage("Error uploading resources.");
    }
    finally{setLoading(false)}
  };

  return (
    <div className="upload-resources-container">
      <h1>Upload Resources for Assessment</h1>
      <p>Ensure the syllabus and all resource files are uploaded in one go.</p>

      <form onSubmit={handleUpload}>
        <label>
          Upload Syllabus:
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setSyllabus(e.target.files[0])}
            required
          />
        </label>
        <label>
          Upload Additional Resources:
          <input
            type="file"
            accept="application/pdf"
            multiple
            onChange={(e) => setResourceFiles(Array.from(e.target.files))}
          />
        </label>
        <button type="submit">Upload All</button>
      </form>

      {message && <p className="upload-message">{message}</p>}
    </div>
  );
}

export default UploadResources;