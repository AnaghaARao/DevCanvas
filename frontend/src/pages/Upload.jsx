import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/general.css";
import "../styles/upload.css";
import BoltIcon from "@mui/icons-material/Bolt";
import { useDispatch, useSelector } from "react-redux";
import { showAlert, showError, showSuccess } from "../hooks/toastUtils";

const Upload = () => {
  const [files, setFiles] = useState([]);
  const [language, setLanguage] = useState("");
  const [docType, setDocType] = useState("");
  const [dirName, setDirName] = useState("");
  const user = useSelector((state) => state.user);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    setFiles((prevFiles) => [...prevFiles, ...e.target.files]);
  };

  const handleFolderChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    if (selectedFiles.length > 0) {
      const firstFilePath = selectedFiles[0].webkitRelativePath;
      const folderName = firstFilePath.split("/")[0];
      setDirName(folderName);
    }
    setFiles((prevFiles) => [...prevFiles, ...selectedFiles]);
  };

  const handleRemoveFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleLanguageChange = (e) => {
    setLanguage(e.target.value);
  };

  const handleDocTypeChange = (e) => {
    setDocType(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (files.length === 0 || !language || !docType || !dirName) {
      showAlert("Please fill all fields and upload a file");
      return;
    }

    const formData = new FormData();
    files.forEach((file) => formData.append("files[]", file));
    formData.append("language", language);
    formData.append("docType", docType);
    formData.append("author", user);
    formData.append("dir_name", dirName);

    try {
      const response = await fetch("http://127.0.0.1:8000/uploadmate/upload/", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (response.ok) {
        if (data.message) {
          showSuccess(data.message);
          const fileUrl = `${import.meta.env.VITE_API_URL}${data.file_url}`;
          console.log(fileUrl);

          navigate("/documentation", {
            state: { fileUrl },
          });
        } else {
          showSuccess("File Upload successfully");
        }
      } else {
        switch (response.status) {
          case 400:
            showError(`Error: ${data.error || "Bad Request"}`);
            break;
          case 404:
            showError(`Error: ${data.error || "File not found"}`);
            break;
          case 500:
            showError(`Error: ${data.error || "Internal server error"}`);
            break;
          default:
            showError(`Error: ${data.error || "Unexpected error"}`);
            break;
        }
      }
    } catch (error) {
      console.error("Error during file upload:", error);
      showError("Error during file upload, please try again");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="upload-form">
      <h2>Upload Files or Folder</h2>
      <hr className="divider" />
      <div className="upload-section">
        <div className="left-upload">
          <div className="upload-files">
            <div className="input-sec">
              <label htmlFor="folderInput">Upload Folder:</label>
              <input
                type="file"
                id="folderInput"
                onChange={handleFolderChange}
                className="input-div"
                accept=".txt, .docx, .pdf, .cpp, .java, .py"
                webkitdirectory="true"
                required
              />
            </div>
          </div>
          {files.length > 0 && (
            <div className="file-list">
              <h3>Uploaded Files: </h3>
              <ul>
                {files.map((file, index) => (
                  <li key={index}>
                    {file.name}
                    <button
                      type="button"
                      onClick={() => handleRemoveFile(index)}
                      className="remove-file-btn"
                    >
                      Remove
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
        <div className="vl"></div>

        <div className="upload-info">
          <div className="language">
            <label htmlFor="languageInput">Programming Language:</label>
            <select
              id="languageInput"
              value={language}
              onChange={handleLanguageChange}
              className="input-div"
              required
            >
              <option value="">Select programming language</option>
              <option value="java">Java</option>
              <option value="python">Python</option>
            </select>
          </div>

          <div className="documentation">
            <label htmlFor="docTypeSelect">Documentation Type:</label>
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

// import React, { useState } from "react";
// import { useNavigate } from "react-router-dom";
// import "../styles/general.css";
// import "../styles/upload.css";
// import BoltIcon from "@mui/icons-material/Bolt";
// import { useDispatch, useSelector } from "react-redux";
// import { showAlert, showError, showSuccess } from "../hooks/toastUtils";

// const Upload = () => {
//   const [file, setFile] = useState(null);
//   const [language, setLanguage] = useState("");
//   const [docType, setDocType] = useState("");
//   const user = useSelector((state) => state.user);
//   const dispatch = useDispatch();
//   const navigate = useNavigate();

//   const handleFileChange = (e) => {
//     setFile(e.target.files[0]);
//   };

//   const handleLanguageChange = (e) => {
//     setLanguage(e.target.value);
//   };

//   const handleDocTypeChange = (e) => {
//     setDocType(e.target.value);
//   };

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     if (!file || !language || !docType) {
//       showAlert("Please fill all fields and upload a file");
//       return;
//     }

//     const formData = new FormData();
//     formData.append("file", file);
//     formData.append("language", language);
//     formData.append("docType", docType);
//     formData.append("author", user);

//     try {
//       const response = await fetch("http://127.0.0.1:8000/uploadmate/upload/", {
//         method: "POST",
//         body: formData,
//       });

//       const data = await response.json();
//       if (response.ok) {
//         if (data.message) {
//           showSuccess(data.message);
//           const fileUrl = `${import.meta.env.VITE_API_URL}${data.file_url}`;
//           console.log(fileUrl);

//           navigate("/documentation", {
//             state: { fileUrl },
//           });
//         } else {
//           showSuccess("File Upload successfully");
//         }
//       } else {
//         switch (response.status) {
//           case 400:
//             showError(`Error: ${data.error || "Bad Request"}`);
//             break;
//           case 404:
//             showError(`Error: ${data.error || "File not found"}`);
//             break;
//           case 500:
//             showError(`Error: ${data.error || "Internal server error"}`);
//             break;
//           default:
//             showError(`Error: ${data.error || "Unexpected error"}`);
//             break;
//         }
//       }
//     } catch (error) {
//       console.error("Error during file upload:", error);
//       showError("Error during file upload, please try again");
//     }
//   };

//   return (
//     <form onSubmit={handleSubmit} className="upload-form">
//       <h2>Upload Files</h2>
//       <hr className="divider" />
//       <div className="upload-section">
//         <div className="upload-files">
//           <label htmlFor="fileInput">Upload File:</label>
//           <input
//             type="file"
//             id="fileInput"
//             onChange={handleFileChange}
//             className="input-div"
//             accept=".txt, .docx, .pdf, .cpp, .java, .py"
//             required
//           />
//         </div>
//         <div className="upload-info">
//           <div className="language">
//             <label htmlFor="languageInput" className="label-head">
//               Programming Language:
//             </label>
//             <input
//               type="text"
//               id="languageInput"
//               value={language}
//               onChange={handleLanguageChange}
//               placeholder="Enter programming language"
//               className="input-div"
//               required
//             />
//           </div>

//           <div className="documentation">
//             <label htmlFor="docTypeSelect" className="label-head">
//               Documentation Type:
//             </label>
//             <select
//               id="docTypeSelect"
//               value={docType}
//               onChange={handleDocTypeChange}
//               className="input-div"
//               required
//             >
//               <option value="">Select documentation type</option>
//               <option value="summary">Summary</option>
//               <option value="class diagram">Class Diagram</option>
//               <option value="sequence diagram">Sequence Diagram</option>
//               <option value="flowchart">Flowchart</option>
//             </select>
//           </div>

//           <button type="submit" className="btn">
//             Generate Now <BoltIcon />
//           </button>
//         </div>
//       </div>
//     </form>
//   );
// };

// export default Upload;
