import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/general.css";
import "../styles/upload.css";
import BoltIcon from "@mui/icons-material/Bolt";

const Upload = () => {
  const [file, setFile] = useState(null);
  const [language, setLanguage] = useState("");
  const [docType, setDocType] = useState("");
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleLanguageChange = (e) => {
    setLanguage(e.target.value);
  };

  const handleDocTypeChange = (e) => {
    setDocType(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !language || !docType) {
      alert("Please fill all fields and upload a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("language", language);
    formData.append("docType", docType);

    try {
      const response = await fetch("http://127.0.0.1:8000/uploadmate/upload/", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        if (data.redirect) {
          if (data.redirect === "summaryGen") {
            alert("Summary generated successfully!");
          } else if (data.redirect === "classDiagram") {
            alert("Class Diagram generated successfully!");
          } else if (data.redirect === "sequenceDiagram") {
            alert("Sequence Diagram generated successfully!");
          } else if (data.redirect === "flowchart") {
            alert("Flowchart generated successfully!");
          } else {
            alert("File uploaded successfully, no specific route to redirect.");
          }
        } else {
          alert("File uploaded successfully.");
        }
      } else {
        // Handle error responses from the backend
        if (data.error) {
          if (data.error === "No file uploaded") {
            alert("Error: No file uploaded. Please try again.");
          } else if (data.error === "Unsupported file type") {
            alert(
              "Error: Unsupported file type. Please upload a supported file."
            );
          } else {
            alert(`Error: ${data.error}`);
          }
        } else if (data.errors) {
          // Handle validation errors
          console.error(data.errors);
          alert("Validation errors occurred. Please check the form data.");
        }
      }
    } catch (error) {
      console.error("Error during file upload:", error);
      alert("Error during file upload, please try again.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="upload-form">
      <h2>Upload Files</h2>
      <hr className="divider" />
      <div className="upload-section">
        <div className="upload-files">
          <label htmlFor="fileInput">Upload File:</label>
          <input
            type="file"
            id="fileInput"
            onChange={handleFileChange}
            className="input-div"
            accept=".txt, .docx, .pdf, .cpp, .java, .py" // Adjust as per allowed file types
            required
          />
        </div>
        <div className="upload-info">
          <div className="language">
            <label htmlFor="languageInput" className="label-head">
              Programming Language:
            </label>
            <input
              type="text"
              id="languageInput"
              value={language}
              onChange={handleLanguageChange}
              placeholder="Enter programming language"
              className="input-div"
              required
            />
          </div>

          <div className="documentation">
            <label htmlFor="docTypeSelect" className="label-head">
              Documentation Type:
            </label>
            {/* <div className="checkbox-inp">
              <input
                type="checkbox"
                name="umlDiagrams"
                checked={docTypes.umlDiagrams}
                onChange={handleCheckboxChange}
                className="checkbox"
              />
              <p>UML Digrams</p>
            </div>
            <div className="checkbox-inp">
              <input
                type="checkbox"
                name="codeSummary"
                checked={docTypes.codeSummary}
                onChange={handleCheckboxChange}
                className="checkbox"
              />
              <p>Code Summary</p>
            </div> */}
            <select
              id="docTypeSelect"
              value={docType}
              onChange={handleDocTypeChange}
              className="input-div"
              required
            >
              <option value="">Select documentation type</option>
              <option value="summary">Summary</option>
              <option value="class diagram">Class Diagram</option>
              <option value="sequence diagram">Sequence Diagram</option>
              <option value="flowchart">Flowchart</option>
            </select>
          </div>

          <button type="submit" className="btn">
            Generate Now <BoltIcon />
          </button>
        </div>
      </div>
    </form>
  );
};

export default Upload;
