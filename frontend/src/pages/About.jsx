import React from "react";
import "../styles/extraPages.css";

const About = () => {
  return (
    <section className="page-container about">
      <h1>About Us</h1>
      <hr className="divider" />
      <p>
        Welcome to our platform!
        <br /> We’re passionate about making software documentation easy,
        accurate, and always up-to-date.
        <br /> Our mission is to empower developers, teams, and organizations by
        automating the documentation process, ensuring that it grows alongside
        your codebase.
        <br /> By streamlining this essential aspect of development, we reduce
        manual effort, increase precision, and improve collaboration. <br />
        Join us on our journey to make code documentation a seamless and
        integral part of software development.
      </p>
      <h2>Our Vision</h2>
      <hr className="divider" />

      <p>
        To revolutionize software development by ensuring every line of code has
        context, clarity, and purpose.
      </p>
      <h2>Our Team</h2>
      <hr className="divider" />

      <p>
        Our team comprises talented engineers, designers, and industry experts
        committed to creating powerful tools that help developers focus on
        building rather than documenting.
      </p>
    </section>
  );
};

export default About;
