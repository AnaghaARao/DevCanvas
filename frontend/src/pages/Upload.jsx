import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/general.css";
import "../styles/upload.css";
import BoltIcon from "@mui/icons-material/Bolt";
import { useDispatch, useSelector } from "react-redux";
import { setUser } from "../store/actions";

const Upload = () => {
  const [file, setFile] = useState(null);
  const [language, setLanguage] = useState("");
  const [docType, setDocType] = useState("");
  const user = useSelector((state) => state.user);
  const dispatch = useDispatch();
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
    formData.append("author", user);

    try {
      const response = await fetch("http://127.0.0.1:8000/uploadmate/upload/", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (response.ok) {
        if (data.message) {
          alert(data.message);
          if (data.summary_path) {
            navigate("/documentation", {
              state: { fileUrl: data.summary_path },
            });
          }
        } else {
          alert("File Upload successfully");
        }
      } else {
        switch (response.status) {
          case 400:
            alert(`Error: ${data.error || "Bad Request"}`);
            break;
          case 404:
            alert(`Error: ${data.error || "File not found"}`);
            break;
          case 500:
            alert(`Error: ${data.error || "Internal server error"}`);
            break;
          default:
            alert(`Error: ${data.error || "Unexpected error"}`);
            break;
        }
      }
    } catch (error) {
      console.error("Error during file upload:", error);
      alert("Error during file upload, please try again");
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
            accept=".txt, .docx, .pdf, .cpp, .java, .py"
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
