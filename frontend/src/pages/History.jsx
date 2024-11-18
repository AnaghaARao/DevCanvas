import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import axios from "axios";
import "../styles/history.css";

const History = () => {
  const [history, setHistory] = useState([]);
  const user = useSelector((state) => state.user);

  useEffect(() => {
    if (user) {
      const fetchHistory = async () => {
        try {
          if (user) {
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
          }

          const response = await axios.post(
            "http://127.0.0.1:8000/uploadmate/history/",
            {
              author: user,
            }
          );
          setHistory(response.data);
        } catch (error) {
          console.error("Error fetching history:", error);
        }
      };

      fetchHistory();
    }
  }, [user]);

  return (
    <div className="history-container">
      <h2>User File History</h2>
      <hr className="divider" />
      {history.map((item, index) => (
        <li key={index} className="history-item">
          <p>{index + 1}.</p>
          <div>
            <div className="file-details">
              <p>
                <span>{item.file_name || "No file name"}</span>
              </p>
              <p className="file-date">
                {item.dateOfGeneration || "No date available"}
              </p>
            </div>
            {item.file_url ? (
              <a href={item.file_url} target="_blank" rel="noopener noreferrer">
                <button className="btn">Click here to view the file</button>
              </a>
            ) : (
              <p>No file available</p>
            )}
          </div>
        </li>
      ))}
    </div>
  );
};

export default History;
