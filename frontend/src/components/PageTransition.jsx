import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import "../styles/pageTransition.css";

const PageTransition = (OgComp) => (props) => {
  return (
    <AnimatePresence mode="popLayout">
      <motion.div
        className="slide-in"
        initial={{ scaleY: 0 }}
        animate={{ scaleY: 1 }}
        exit={{ scaleY: 0 }}
        transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
      >
        <OgComp {...props} />
      </motion.div>
    </AnimatePresence>
  );
};

export default PageTransition;
