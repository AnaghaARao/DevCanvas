import React from "react";
import "../styles/LandingPage/team.css";
import { motion } from "framer-motion";
import ScrollAnimation from "./ScrollAnimation";
import anagha from "/anagha.jpeg";
import anjali from "/anjali.jpg";
import adarsh from "/adarsh.jpeg";
import shivamani from "/shivamani.jpeg";

const Team = () => {
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
        <ScrollAnimation
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <motion.div
            whileHover={{ scale: 1.07 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="team-member"
            href="https://www.linkedin.com/in/scoder17/"
            target="_blank"
          >
            <img src={adarsh} alt="Team Member 1" className="team-img" />
            <div className="member-deets">
              <h3>Adarsh Singh</h3>
              <p>AI Tools Expert</p>
            </div>
          </motion.div>
        </ScrollAnimation>
        <ScrollAnimation
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <motion.div
            whileHover={{ scale: 1.07 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="team-member"
            href="https://www.linkedin.com/in/anaghaarao/"
            target="_blank"
          >
            <img src={anagha} alt="Team Member 2" className="team-img" />
            <div className="member-deets">
              <h3>Anagha A Rao</h3>
              <p>Backend Developer</p>
            </div>
          </motion.div>
        </ScrollAnimation>
        <ScrollAnimation
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <motion.div
            whileHover={{ scale: 1.07 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="team-member"
            href="https://www.linkedin.com/in/anjali-bhatkal-5802801b7/"
            target="_blank"
          >
            <img src={anjali} alt="Team Member 3" className="team-img" />
            <div className="member-deets">
              <h3>Anjali Bhatkal</h3>
              <p>Frontend Developer</p>
            </div>
          </motion.div>
        </ScrollAnimation>
        <ScrollAnimation
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <motion.div
            whileHover={{ scale: 1.07 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="team-member"
            href="https://www.linkedin.com/in/shivamanik/"
            target="_blank"
          >
            <img src={shivamani} alt="Team Member 4" className="team-img" />
            <div className="member-deets">
              <h3>Shiva Mani K</h3>
              <p>Algorithms Engineer</p>
            </div>
          </motion.div>
        </ScrollAnimation>
      </div>
    </div>
  );
};

export default Team;
