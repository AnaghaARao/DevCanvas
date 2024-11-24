import React from "react";
import { motion } from "framer-motion";
import ScrollAnimation from "./ScrollAnimation";
import "../styles/LandingPage/services.css";

const Services = () => {
  return (
    <div className="lp-services">
      <ScrollAnimation
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 1, ease: "easeInOut" }}
      >
        <motion.h2>Our Services</motion.h2>
      </ScrollAnimation>

      <ScrollAnimation
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
      >
        <motion.div className="service-list">
          <ScrollAnimation
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.6 }}
          >
            <motion.p>Automated code documentation generation</motion.p>
          </ScrollAnimation>
          <ScrollAnimation
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <motion.p>Real-time updates on software changes</motion.p>
          </ScrollAnimation>
          <ScrollAnimation
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.6 }}
          >
            <motion.p>Customizable documentation formats</motion.p>
          </ScrollAnimation>
          <ScrollAnimation
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.9 }}
          >
            <motion.p>Language support for Java & Python</motion.p>
          </ScrollAnimation>
        </motion.div>
      </ScrollAnimation>
    </div>
  );
};

export default Services;
