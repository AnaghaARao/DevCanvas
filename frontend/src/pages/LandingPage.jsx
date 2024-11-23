import React from "react";
import "../styles/landing.css";
import Footer from "../components/Footer";
import Intro from "../components/Intro";
import Process from "../components/Process";

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
      <div className="lp-motivation">
        <h2>Our Motivation</h2>
        <p>
          Maintaining accurate and up-to-date documentation is essential, yet
          often neglected due to the focus on coding. Our tool automates the
          documentation process, keeping it in sync with the evolving codebase.
          This reduces manual effort, enhances accuracy, and fosters
          collaboration among developers and stakeholders.
        </p>
      </div>
      <hr className="divider" />
      <div className="lp-team">
        <h2>Meet the Team</h2>
        <div className="team-members">
          <div className="team-member">
            <img src="team-member1.jpg" alt="Team Member 1" />
            <h3>Team Member 1</h3>
            <p>Role</p>
          </div>
          <div className="team-member">
            <img src="team-member2.jpg" alt="Team Member 2" />
            <h3>Team Member 2</h3>
            <p>Role</p>
          </div>
          <div className="team-member">
            <img src="team-member3.jpg" alt="Team Member 3" />
            <h3>Team Member 3</h3>
            <p>Role</p>
          </div>
        </div>
      </div>
      <hr className="divider" />
      <div className="lp-services">
        <h2>Our Services</h2>
        <ul>
          <li>Automated code documentation generation</li>
          <li>Real-time updates on software changes</li>
          <li>Customizable documentation formats</li>
          <li>Multi-language support (Java, Python, etc.)</li>
        </ul>
      </div>
      <hr className="divider" />
      <div className="lp-faqs">
        <h2>Frequently Asked Questions</h2>
        <div className="faq-item">
          <h3>What programming languages do you support?</h3>
          <p>
            Currently, we support Java and Python. More languages are coming
            soon.
          </p>
        </div>
        <div className="faq-item">
          <h3>Is my code data secure?</h3>
          <p>
            Yes, all code uploaded is handled securely with encryption and
            access control.
          </p>
        </div>
        <div className="faq-item">
          <h3>How often is the documentation updated?</h3>
          <p>
            Documentation updates in real-time, reflecting any changes made in
            the codebase.
          </p>
        </div>
      </div>
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
