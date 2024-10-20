import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
// import "../styles/output.css";

const Output = () => {
  const { docType, docId } = useParams();
  const [fileUrl, setFileUrl] = useState("");

  useEffect(() => {
    // Fetch the file URL based on the document ID and type
    const fetchFile = async () => {
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/uploadmate/download/${docId}/`
        );
        const data = await response.json();

        if (response.ok) {
          setFileUrl(data.file_url); // Assuming file_url is returned by the backend
        } else {
          console.error("Failed to fetch file:", data);
        }
      } catch (error) {
        console.error("Error fetching file:", error);
      }
    };

    fetchFile();
  }, [docId]);

  return (
    <div className="output-container">
      <h2>{docType} Generated</h2>
      {fileUrl ? (
        <>
          <a href={fileUrl} download className="download-btn">
            Download {docType}
          </a>
        </>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
};

export default Output;
