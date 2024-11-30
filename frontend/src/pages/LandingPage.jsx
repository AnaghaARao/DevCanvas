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
import process from "/processpic.jpg";
import { Parallax } from "react-parallax";

function LandingPage() {
  return (
    <div className="lp-container">
      <Intro />
      <hr className="divider" />
      <Parallax
        bgImage={process}
        strength={500}
        bgImageStyle={{ opacity: 0.7 }}
      >
        <div className="process-container">
          <Process
            steps={[
              "Upload",
              "Generate UML",
              "View Summary",
              "Navigate",
              "Understand",
              "Code",
            ]}
          />
        </div>
      </Parallax>

      <hr className="divider" />
      <Motivation />
      <Parallax
        bgImage={process}
        strength={500}
        bgImageStyle={{ opacity: 0.7 }}
      >
        <div className="services-container">
          <Services />
        </div>
      </Parallax>
      <FAQS />
      <hr className="divider" />
      <Team />
      <Parallax
        bgImage={process}
        strength={500}
        bgImageStyle={{ opacity: 0.7 }}
      >
        <div className="security-container">
          <Security />
        </div>
      </Parallax>
      <Footer />
    </div>
  );
}

export default LandingPage;
