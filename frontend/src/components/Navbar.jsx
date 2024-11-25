import React, { useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { useLocation, Link, useNavigate } from "react-router-dom";
import { clearUser } from "../store/actions";
import "../styles/navbar.css";
import { motion } from "framer-motion";

const MotionLink = motion.create(Link);

function Navbar() {
  const user = useSelector((state) => state.user);
  const location = useLocation();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [isMobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    dispatch(clearUser());
    navigate("/");
  };

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <div className="navbar">
      <Link to="/" className="navbar-logo">
        <img src="/logo.png" alt="Logo" />
        <h2 className="logo-title">DevCanvas</h2>
      </Link>

      <div className="navbar-links">
        {user ? (
          <div className="home-upload-history">
            <MotionLink
              className={`navbar-item ${
                location.pathname === "/" ? "active" : ""
              }`}
              to="/"
              whileHover={{ scale: 1.1 }}
            >
              Home
            </MotionLink>
            <MotionLink
              className={`navbar-item ${
                location.pathname === "/main" ? "active" : ""
              }`}
              to="/main"
              whileHover={{ scale: 1.1 }}
            >
              Upload
            </MotionLink>
            <MotionLink
              className={`navbar-item ${
                location.pathname === "/upload-history" ? "active" : ""
              }`}
              to="/upload-history"
              whileHover={{ scale: 1.1 }}
            >
              History
            </MotionLink>
          </div>
        ) : (
          location.pathname === "/" && (
            <>
              <MotionLink
                className="navbar-item"
                to="/authentication/login"
                whileHover={{ scale: 1.1 }}
              >
                Login
              </MotionLink>
              <MotionLink
                className="navbar-item"
                to="/authentication/register"
                whileHover={{ scale: 1.1 }}
              >
                Register
              </MotionLink>
            </>
          )
        )}
      </div>

      {user && (
        <div className="logout">
          <p className="navbar-user">
            Hello, <span className="navbar-name">{user}</span>
          </p>
          <button className="navbar-btn" onClick={handleLogout}>
            Logout
          </button>
        </div>
      )}

      <div className="hamburger" onClick={toggleMobileMenu}>
        {isMobileMenuOpen ? "✖" : "☰"}
      </div>

      {isMobileMenuOpen && (
        <div className="mobile-menu">
          {user ? (
            <>
              <Link
                className="mobile-menu-item"
                to="/"
                onClick={toggleMobileMenu}
              >
                Home
              </Link>
              <Link
                className="mobile-menu-item"
                to="/main"
                onClick={toggleMobileMenu}
              >
                Upload
              </Link>
              <Link
                className="mobile-menu-item"
                to="/upload-history"
                onClick={toggleMobileMenu}
              >
                History
              </Link>
              <Link className="mobile-menu-item" to="/" onClick={handleLogout}>
                Logout
              </Link>
            </>
          ) : (
            <>
              <Link
                className="mobile-menu-item"
                to="/authentication/login"
                onClick={toggleMobileMenu}
              >
                Login
              </Link>
              <Link
                className="mobile-menu-item"
                to="/authentication/register"
                onClick={toggleMobileMenu}
              >
                Register
              </Link>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default Navbar;
