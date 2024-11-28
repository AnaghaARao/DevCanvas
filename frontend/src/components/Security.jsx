import React from "react";
import "../styles/LandingPage/security.css";
import { motion } from "framer-motion";
import ScrollAnimation from "./ScrollAnimation"; // Import the reusable ScrollAnimation component

const Security = () => {
  return (
    <div className="lp-security">
      <ScrollAnimation
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeInOut" }}
      >
        <motion.h2>Security</motion.h2>
      </ScrollAnimation>
      <ScrollAnimation
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.8, delay: 0.2, ease: "easeInOut" }}
      >
        <motion.p>
          We prioritize the security of your data. <br />
          Our platform uses SSL encryption for data transmission, and all
          uploaded code is stored securely with access restrictions to ensure
          your intellectual property remains safe. <br />
          We automatically delete your codebase 10 seconds after you click the
          "Generate Now" button.
        </motion.p>
      </ScrollAnimation>
    </div>
  );
};

export default Security;
