import React, { useState } from "react";
import "../styles/general.css";
import "../styles/upload.css";
import BoltIcon from "@mui/icons-material/Bolt";

const Upload = () => {
  const [file, setFile] = useState(null);
  const [language, setLanguage] = useState("");
  const [docTypes, setDocTypes] = useState({
    umlDiagrams: false,
    codeSummary: false,
  });

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleLanguageChange = (e) => {
    setLanguage(e.target.value);
  };

  const handleCheckboxChange = (e) => {
    const { name, checked } = e.target;
    setDocTypes((prev) => ({
      ...prev,
      [name]: checked,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !language) {
      alert("Please fill all fields and upload a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("language", language);
    formData.append("umlDiagrams", docTypes.umlDiagrams);
    formData.append("codeSummary", docTypes.codeSummary);
    formData.append("dateTime", new Date().toISOString());
    formData.append("author", "Anjali Uday Bhatkal"); // Assuming author is hardcoded, you can make this dynamic if needed.

    try {
      const response = await fetch("/uploadmate/upload/", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();

      if (response.ok) {
        console.log("File uploaded successfully");
      } else {
        console.error(data.error);
      }
    } catch (error) {
      console.error("Error during file upload:", error);
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
            <label className="label-head">Documentation Type:</label>
            <div className="checkbox-inp">
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
            </div>
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
