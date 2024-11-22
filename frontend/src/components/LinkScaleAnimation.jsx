import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";

const MotionLink = motion(Link);

const LinkScaleAnimation = ({ to, onClick, children, className }) => (
  <MotionLink
    to={to}
    onClick={onClick}
    className={className}
    whileHover={{ scale: 1.1 }}
    whileTap={{ scale: 0.9 }}
  >
    {children}
  </MotionLink>
);

export default LinkScaleAnimation;
