import React from "react";
import "../styles/landing.css";
import lp from "../../src/landing.png";

function LandingPage() {
  return (
    <div className="lp-container">
      <div className="lp-sec1">
        <div className="lp-content">
          <h1>Organize your code and visualize its structure!</h1>
          <p>Generate UML diagrams and summary for code files.</p>
          <button className="btn">Start Now</button>
        </div>
        <img src={lp} alt="Landing page" className="lp-img" />
      </div>
      <hr className="divider" />

      <div className="lp-sec2">
        <div className="item-group">
          <div className="item">
            <p className="item-circle">1</p>
            <p className="item-title">Upload</p>
          </div>
          <div className="item">
            <p className="item-circle">2</p>
            <p className="item-title">Generate URL</p>
          </div>
          <div className="item">
            <p className="item-circle">3</p>
            <p className="item-title">View Summary</p>
          </div>
          <div className="item">
            <p className="item-circle">4</p>
            <p className="item-title">Navigate</p>
          </div>
          <div className="item">
            <p className="item-circle">5</p>
            <p className="item-title">Understand</p>
          </div>
          <div className="item">
            <p className="item-circle">6</p>
            <p className="item-title">Code</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LandingPage;
