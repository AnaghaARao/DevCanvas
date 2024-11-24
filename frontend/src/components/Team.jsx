import React from "react";
import "../styles/LandingPage/team.css";
import { motion } from "framer-motion";
import ScrollAnimation from "./ScrollAnimation"; // Import the reusable ScrollAnimation component

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
          >
            <img src="team-member1.jpg" alt="Team Member 1" />
            <h3>Adarsh Singh</h3>
            <p>Role</p>
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
          >
            <img src="team-member2.jpg" alt="Team Member 2" />
            <h3>Anagha A Rao</h3>
            <p>Backend Developer</p>
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
          >
            <img src="team-member3.jpg" alt="Team Member 3" />
            <h3>Anjali Bhatkal</h3>
            <p>Frontend Developer</p>
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
          >
            <img src="team-member4.jpg" alt="Team Member 4" />
            <h3>Shiva Mani K</h3>
            <p>Role</p>
          </motion.div>
        </ScrollAnimation>
      </div>
    </div>
  );
};

export default Team;
