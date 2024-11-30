import React from "react";
import "../styles/LandingPage/team.css";
import { motion } from "framer-motion";
import ScrollAnimation from "./ScrollAnimation";
import anagha from "/anagha.jpeg";
import anjali from "/anjali.jpg";
import adarsh from "/adarsh.jpg";
import shivamani from "/shivamani.jpeg";

const Team = () => {
  const teamMembers = [
    {
      name: "Adarsh Singh",
      role: "Lead Researcher & Engineer",
      image: adarsh,
      linkedin: "https://www.linkedin.com/in/scoder17/",
    },
    {
      name: "Anagha A Rao",
      role: "Backend Developer",
      image: anagha,
      linkedin: "https://www.linkedin.com/in/anaghaarao/",
    },
    {
      name: "Anjali Bhatkal",
      role: "Frontend Developer",
      image: anjali,
      linkedin: "https://www.linkedin.com/in/anjali-bhatkal-5802801b7/",
    },
    {
      name: "Shiva Mani K",
      role: "Algorithms Engineer",
      image: shivamani,
      linkedin: "https://www.linkedin.com/in/shivamanik/",
    },
  ];

  return (
    <div className="lp-team">
      <ScrollAnimation
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeInOut" }}
      >
        <motion.h2>Meet the Team</motion.h2>
      </ScrollAnimation>
      <div className="team-members">
        {teamMembers.map((member, index) => (
          <ScrollAnimation
            key={index}
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <motion.a
              whileHover={{ scale: 1.07 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
              className="team-member"
              href={member.linkedin}
              target="_blank"
              rel="noopener noreferrer"
            >
              <img
                src={member.image}
                alt={`${member.name}`}
                className="team-img"
              />
              <div className="member-deets">
                <h3>{member.name}</h3>
                <p>{member.role}</p>
              </div>
            </motion.a>
          </ScrollAnimation>
        ))}
      </div>
    </div>
  );
};

export default Team;
