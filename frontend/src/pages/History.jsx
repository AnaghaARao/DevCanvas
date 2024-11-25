import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "../styles/history.css";
import Footer from "../components/Footer";

const History = () => {
  const [history, setHistory] = useState([]);
  const [filteredHistory, setFilteredHistory] = useState([]);
  const [searchItem, setSearchItem] = useState("");
  const [filterType, setFilterType] = useState("");

  const user = useSelector((state) => state.user);
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      const fetchHistory = async () => {
        try {
          const response = await axios.post(
            "http://127.0.0.1:8000/docify/history/",
            {
              author: user,
            }
          );

          if (response.data && Array.isArray(response.data.files)) {
            const filteredFiles = response.data.files.filter(
              (file) => !file.file_name.toLowerCase().endsWith(".png")
            );
            setHistory(filteredFiles);
            setFilteredHistory(filteredFiles); // Initialize filteredHistory
          } else {
            console.error("Received data is not an array:", response.data);
            setHistory([]);
            setFilteredHistory([]);
          }
        } catch (error) {
          console.error("Error fetching history:", error);
        }
      };

      fetchHistory();
    }
  }, [user]);

  useEffect(() => {
    const filterAndSearchFiles = () => {
      let files = history;

      // Apply type filter if selected
      if (filterType) {
        files = files.filter((file) =>
          file.file_name.toLowerCase().startsWith(filterType.toLowerCase())
        );
      }

      // Apply search filter if search item exists
      if (searchItem) {
        files = files.filter((file) =>
          file.file_name.toLowerCase().includes(searchItem.toLowerCase())
        );
      }

      setFilteredHistory(files);
    };

    filterAndSearchFiles();
  }, [history, searchItem, filterType]);

  const handleViewFile = (fileUrl) => {
    fileUrl = `${import.meta.env.VITE_API_URL}${fileUrl}`;
    navigate("/documentation", { state: { fileUrl } });
  };

  const formatDate = (dateString) => {
    if (!dateString) return "No date available";

    const date = new Date(dateString);
    return date.toLocaleString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "numeric",
      minute: "numeric",
      hour12: true,
    });
  };

  return (
    <div>
      <div className="history-container">
        <h2>User File History</h2>
        <hr className="divider" />

        <div className="history-search">
          <input
            type="text"
            placeholder="Search for a file"
            value={searchItem}
            onChange={(e) => setSearchItem(e.target.value)}
            className="history-search"
          />
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="history-dropdown"
          >
            <option value="">All</option>
            <option value="summary">Summary</option>
            <option value="class_diagram">Class Diagram</option>
            <option value="flowchart">Flowchart</option>
            <option value="sequence_diagram">Sequence Diagram</option>
          </select>
        </div>

        {Array.isArray(filteredHistory) && filteredHistory.length > 0 ? (
          <ul>
            {filteredHistory.map((item, index) => (
              <li key={index} className="history-item">
                <p>{index + 1}.</p>
                <div className="main-file">
                  <p className="file-details">
                    <span>{item.file_name || "No file name"}</span>
                  </p>
                  <div className="file-details">
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
                    <p className="file-date">
                      {item.dateOfGeneration
                        ? formatDate(item.dateOfGeneration)
                        : "No date available"}
                    </p>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p>No history available.</p>
        )}
      </div>
      <Footer />
    </div>
  );
};

export default History;
