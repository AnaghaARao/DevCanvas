import React from "react";
import "../styles/extraPages.css";
import "../components/Footer.jsx";
import Footer from "../components/Footer.jsx";

const About = () => {
  return (
    <section>
      <div className="page-container about">
        <h1 className="main-heading">About Us</h1>
        <hr className="divider" />
        <p>
          Welcome to our platform!
          <br /> We’re passionate about making software documentation easy,
          accurate, and always up-to-date.
          <br /> Our mission is to empower developers, teams, and organizations
          by automating the documentation process, ensuring that it grows
          alongside your codebase.
          <br /> By streamlining this essential aspect of development, we reduce
          manual effort, increase precision, and improve collaboration. <br />
          Join us on our journey to make code documentation a seamless and
          integral part of software development.
        </p>
        <div>
          <h2>Our Vision</h2>
          <p>
            To revolutionize software development by ensuring every line of code
            has context, clarity, and purpose.
          </p>
        </div>
        <div>
          <h2>Our Team</h2>
          <p>
            Our team comprises talented engineers, designers, and industry
            experts committed to creating powerful tools that help developers
            focus on building rather than documenting.
          </p>
        </div>
        <hr className="divider" />
      </div>
      <Footer />
    </section>
  );
};

export default About;
