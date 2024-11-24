// ScrollAnimation.js
import React, { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";

const ScrollAnimation = ({ children, initial, animate, transition }) => {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current);
      }
    };
  }, []);

  return (
    <motion.div
      ref={ref}
      initial={initial}
      animate={isVisible ? animate : initial}
      transition={transition}
    >
      {children}
    </motion.div>
  );
};

export default ScrollAnimation;
