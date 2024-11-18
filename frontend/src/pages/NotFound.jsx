import React from "react";
import "../styles/general.css";

function NotFound() {
  return (
    <div className="notfound-container">
      <h1>
        Oops! <span>404</span> Not Found.
      </h1>
      <hr className="divider"></hr>
      <p>The page you're looking for doesn't exist!</p>
    </div>
  );
}

export default NotFound;
