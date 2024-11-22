import React from "react";
import { useNavigate } from "react-router-dom";
import lp from "../../src/landing.png";
import "../styles/landing.css";
import { useSelector } from "react-redux";
import { motion } from "framer-motion";

function LandingPage() {
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
    <div className="lp-container">
      <motion.div
        className="lp-sec1"
        initial="hidden"
        animate="visible"
        transition={{ staggerChildren: 0.3 }}
      >
        <div className="lp-content">
          <motion.h1
            initial={{ x: -100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            Organize your code and visualize its structure!
          </motion.h1>
          <motion.p
            initial={{ x: -100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            Generate UML diagrams and summary for code files.
          </motion.p>
          <motion.button
            className="btn"
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

      <hr className="divider" />

      <motion.div
        className="lp-sec2"
        initial="hidden"
        animate="visible"
        transition={{ staggerChildren: 0.2 }}
      >
        <div className="item-group">
          {[
            "Upload",
            "Generate URL",
            "View Summary",
            "Navigate",
            "Understand",
            "Code",
          ].map((title, index) => (
            <motion.div
              key={index}
              className="item"
              variants={{
                hidden: { opacity: 0, y: 20 },
                visible: { opacity: 1, y: 0 },
              }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            >
              <p className="item-circle">{index + 1}</p>
              <p className="item-title">{title}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}

export default LandingPage;
