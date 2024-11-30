import React from "react";
import "../styles/footer.css";

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-section">
          <h3>About Us</h3>
          <p>
            At DevCanvas, we strive to transform the way software documentation
            is created. Our goal is to simplify and automate the entire process,
            enabling developers to focus more on coding and less on writing
            documentation. By harnessing the power of AI, we create real-time,
            precise, and contextually relevant documentation tailored to each
            project. We are passionate about making the documentation process
            faster, smarter, and more efficient.
          </p>
        </div>

        <div className="footer-section2">
          <h3>Quick Links</h3>
          <ul>
            <li>
              <a href="/about">About</a>
            </li>
            <li>
              <a href="/services">Services</a>
            </li>
            {/* <li>
              <a href="/contact">Contact</a>
            </li> */}
            <li>
              <a href="/privacy-policy">Privacy Policy</a>
            </li>
            <li>
              <a href="/terms-of-service">Terms of Service</a>
            </li>
          </ul>
        </div>

        {/* <div className="footer-section">
          <h3>Follow Us</h3>
          <div className="social-links">
            <a
              href="https://facebook.com"
              target="_blank"
              rel="noopener noreferrer"
            >
              <i className="fab fa-facebook"></i>
            </a>
            <a
              href="https://twitter.com"
              target="_blank"
              rel="noopener noreferrer"
            >
              <i className="fab fa-twitter"></i>
            </a>
            <a
              href="https://linkedin.com"
              target="_blank"
              rel="noopener noreferrer"
            >
              <i className="fab fa-linkedin"></i>
            </a>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
            >
              <i className="fab fa-github"></i>
            </a>
          </div>
        </div> */}
      </div>
      <div className="footer-bottom">
        <p>&copy; {new Date().getFullYear()} DevCanvas. All Rights Reserved.</p>
      </div>
    </footer>
  );
}

export default Footer;
