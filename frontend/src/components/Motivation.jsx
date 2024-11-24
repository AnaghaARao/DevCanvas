import React from "react";
import "../styles/LandingPage/motivation.css";
import { easeInOut, motion } from "framer-motion";
import ScrollAnimation from "./ScrollAnimation"; // Import the reusable component

const Motivation = () => {
  return (
    <ScrollAnimation
      initial={{ y: -50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 1, ease: easeInOut }}
    >
      <div className="lp-motivation">
        <motion.h2>Why choose devcanvas?</motion.h2>
        <motion.p
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.2, ease: easeInOut }}
        >
          Accurate, up-to-date documentation is crucial for software success but
          often neglected.
        </motion.p>
        <motion.p
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.4, ease: easeInOut }}
        >
          Our tool auto-generates documentation, keeping it in sync with your
          codebase and eliminating the need for manual updates.
        </motion.p>
        <motion.p
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.6, ease: easeInOut }}
        >
          This enhances accuracy, accelerates development cycles, improves team
          collaboration, and provides stakeholders with real-time insights,
          making documentation a powerful driver of efficiency and innovation,
          not an afterthought.
        </motion.p>
      </div>
    </ScrollAnimation>
  );
};

export default Motivation;
