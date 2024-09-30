import React, { useState } from "react";

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
      <div>
        <label htmlFor="fileInput">Upload File:</label>
        <input
          type="file"
          id="fileInput"
          onChange={handleFileChange}
          accept=".txt, .docx, .pdf, .cpp, .java, .py" // Adjust as per allowed file types
          required
        />
      </div>

      <div>
        <label htmlFor="languageInput">Programming Language:</label>
        <input
          type="text"
          id="languageInput"
          value={language}
          onChange={handleLanguageChange}
          placeholder="Enter programming language"
          required
        />
      </div>

      <div>
        <label>Documentation Type:</label>
        <div>
          <label>
            <input
              type="checkbox"
              name="umlDiagrams"
              checked={docTypes.umlDiagrams}
              onChange={handleCheckboxChange}
            />
            UML Diagrams
          </label>
        </div>
        <div>
          <label>
            <input
              type="checkbox"
              name="codeSummary"
              checked={docTypes.codeSummary}
              onChange={handleCheckboxChange}
            />
            Code Summary
          </label>
        </div>
      </div>

      <button type="submit">Generate Now</button>
    </form>
  );
};

export default Upload;
