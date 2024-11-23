import React from "react";
import "../styles/landing.css";
import Footer from "../components/Footer";
import Intro from "../components/Intro";
import Process from "../components/Process";
import Motivation from "../components/Motivation";
import Team from "../components/Team";
import Services from "../components/Services";
import FAQS from "../components/FAQS";

function LandingPage() {
  return (
    <div className="lp-container">
      <Intro />
      <hr className="divider" />
      <Process
        steps={[
          "Upload",
          "Generate URL",
          "View Summary",
          "Navigate",
          "Understand",
          "Code",
        ]}
      />
      <hr className="divider" />
      <Motivation />
      <Team />
      <Services />
      <FAQS />
      <hr className="divider" />

      <div className="lp-security">
        <h2>Security</h2>
        <p>
          We prioritize the security of your data. Our platform uses SSL
          encryption for data transmission, and all uploaded code is stored
          securely with access restrictions to ensure your intellectual property
          remains safe.
        </p>
      </div>

      <Footer />
    </div>
  );
}

export default LandingPage;
