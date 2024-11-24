import React, { useState } from "react";
import "../styles/LandingPage/faqs.css";
import ArrowDropUpIcon from "@mui/icons-material/ArrowDropUp";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import { easeInOut, motion } from "framer-motion";

const FAQS = () => {
  const [activeIndex, setActiveIndex] = useState(null);

  const toggleFAQ = (index) => {
    setActiveIndex(activeIndex === index ? null : index);
  };

  const faqData = [
    {
      question: "What programming languages do you support?",
      answer:
        "Currently, we support Java and Python. More languages are coming soon.",
    },
    {
      question: "Is my code data secure?",
      answer:
        "Yes, all code uploaded is handled securely with encryption and access control.",
    },
    {
      question: "How often is the documentation updated?",
      answer:
        "Documentation updates in real-time, reflecting any changes made in the codebase.",
    },
    {
      question: "Do I need an internet connection to use this tool?",
      answer:
        "An internet connection is required for certain features, such as real-time updates and cloud storage access.",
    },
    {
      question: "Is there a mobile version available?",
      answer:
        "We currently support a desktop version, but a mobile app is in development and will be released soon.",
    },
    {
      question: "How can I report bugs or request new features?",
      answer:
        "You can reach out to us through the feedback form on our website or via email. We welcome all feedback and suggestions!",
    },
    {
      question: "What is the pricing model for this tool?",
      answer:
        "We offer both free and premium plans. The free plan includes basic features, while the premium plan offers additional features and priority support.",
    },
    {
      question: "How do I get started with this tool?",
      answer:
        "Simply create an account, and you'll be guided through a quick setup process. Our documentation also provides detailed steps for getting started.",
    },
    {
      question: "Can I collaborate with others on my projects?",
      answer:
        "Yes, the premium version allows for team collaboration with features like shared access and project tracking.",
    },
  ];

  return (
    <div className="lp-faqs">
      <motion.h2
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: easeInOut }}
      >
        FAQs
      </motion.h2>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: easeInOut }}
        className="faq-list"
      >
        {faqData.map((item, index) => (
          <div
            key={index}
            className={`faq-item ${activeIndex === index ? "active" : ""}`}
            onClick={() => toggleFAQ(index)}
          >
            <div className="faq-question">
              <h3>{item.question}</h3>
              {activeIndex === index ? (
                <ArrowDropUpIcon className="icon" />
              ) : (
                <ArrowDropDownIcon className="icon" />
              )}
            </div>
            <div className="faq-answer">
              <p>{item.answer}</p>
            </div>
          </div>
        ))}
      </motion.div>
    </div>
  );
};

export default FAQS;
