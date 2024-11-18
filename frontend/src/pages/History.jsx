import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import axios from "axios";

const History = () => {
  const [history, setHistory] = useState([]);
  const user = useSelector((state) => state.user);

  useEffect(() => {
    if (user) {
      const fetchHistory = async () => {
        try {
          const response = await axios.post("uploadMate/history/", {
            author: user,
          });
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
      {history.length > 0 ? (
        <ul>
          {history.map((item, index) => (
            <li key={index}>
              <p>File Name: {item.file_name}</p>
              <p>Date of Generation: {item.dateOfGeneration}</p>
              <p>
                File URL:{" "}
                <a
                  href={item.file_url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {item.file_url}
                </a>
              </p>
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
