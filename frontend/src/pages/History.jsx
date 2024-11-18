import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "../styles/history.css";

const History = () => {
  const [history, setHistory] = useState([]);
  const user = useSelector((state) => state.user);
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      const fetchHistory = async () => {
        try {
          if (typeof user === "string") {
            console.log("User is a string:", user);
          } else if (typeof user === "object") {
            if (Array.isArray(user)) {
              console.log("User is an array:", user);
            } else {
              console.log("User is an object:", user);
            }
          } else {
            console.log("User type is unknown:", typeof user);
          }

          const response = await axios.post(
            "http://127.0.0.1:8000/uploadmate/history/",
            {
              author: user,
            }
          );

          console.log(response.data);
          if (response.data && Array.isArray(response.data.files)) {
            setHistory(response.data.files);
            console.log("history has been set");
          } else {
            console.error("Received data is not an array:", response.data);
            setHistory([]);
          }
        } catch (error) {
          console.error("Error fetching history:", error);
        }
      };

      fetchHistory();
    }
  }, [user]);

  const handleViewFile = (fileUrl) => {
    navigate("/documentation", { state: { fileUrl } });
  };

  return (
    <div className="history-container">
      <h2>User File History</h2>
      <hr className="divider" />
      {Array.isArray(history) && history.length > 0 ? (
        <ul>
          {history.map((item, index) => (
            <li key={index} className="history-item">
              <p>{index + 1}.</p>
              <div className="main-file">
                <div className="file-details">
                  <p>
                    <span>{item.file_name || "No file name"}</span>
                  </p>
                  <p className="file-date">
                    {item.dateOfGeneration || "No date available"}
                  </p>
                </div>
                {item.file_url ? (
                  <button
                    className="btn history-btn"
                    onClick={() => handleViewFile(item.file_url)}
                  >
                    Click here to view the file
                  </button>
                ) : (
                  <p>No file available</p>
                )}
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p>No history available.</p>
      )}
    </div>
  );
};

export default History;
