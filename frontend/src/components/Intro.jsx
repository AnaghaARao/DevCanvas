import React from "react";
import lp from "/intropic.png";
import { useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import "../styles/LandingPage/intro.css";
import { motion } from "framer-motion";

const Intro = () => {
  const navigate = useNavigate();
  const user = useSelector((state) => state.user);
  console.log("User in LandingPage:", user);

  const handleStartNow = () => {
    if (user != null) {
      navigate("/main");
    } else {
      navigate("authentication/register");
    }
  };
  return (
    <div className="intro-container">
      <motion.div
        className="lp-sec1"
        initial="hidden"
        animate="visible"
        transition={{ staggerChildren: 0.3 }}
      >
        <div className="lp-content">
          <motion.h1
            initial={{ x: -150, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            Organize your code and visualize its structure!
          </motion.h1>
          <motion.p
            initial={{ x: -150, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            Generate UML diagrams and summary for code files.
          </motion.p>
          <motion.button
            className="btn start"
            onClick={handleStartNow}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            Start Now
          </motion.button>
        </div>
        <motion.img
          src={lp}
          alt="Landing page"
          className="lp-img"
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
      </motion.div>
    </div>
  );
};

export default Intro;
