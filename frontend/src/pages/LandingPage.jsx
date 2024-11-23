import React from "react";
import "../styles/landing.css";
import Footer from "../components/Footer";
import Intro from "../components/Intro";
import Process from "../components/Process";
import Motivation from "../components/Motivation";
import Team from "../components/Team";
import Services from "../components/Services";
import FAQS from "../components/FAQS";
import Security from "../components/Security";

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
      <Services />
      <FAQS />
      <hr className="divider" />
      <Team />
      <Security />
      <Footer />
    </div>
  );
}

export default LandingPage;
