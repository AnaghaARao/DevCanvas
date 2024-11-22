import React, { useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { useLocation, Link, useNavigate } from "react-router-dom";
import { clearUser } from "../store/actions";
import "../styles/navbar.css";
import LinkScaleAnimation from "./LinkScaleAnimation";

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

  const isLandingPage = location.pathname === "/";
  const isLoginPage = location.pathname === "/authentication/login";
  const isRegisterPage = location.pathname === "/authentication/register";

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <div className="navbar">
      <Link to="/" className="navbar-logo">
        <img src="/logo.png" alt="Logo" />
        <h2 className="logo-title">DevCanvas</h2>
      </Link>

      <div className="notMobile">
        <div className="navbar-links">
          {isLandingPage && !user ? (
            <>
              <LinkScaleAnimation
                className="navbar-item"
                to="/authentication/login"
              >
                Login
              </LinkScaleAnimation>
              <LinkScaleAnimation
                className="navbar-item"
                to="/authentication/register"
              >
                Register
              </LinkScaleAnimation>
            </>
          ) : (
            !isLoginPage &&
            !isRegisterPage && (
              <div className="home-upload-history">
                <LinkScaleAnimation className="navbar-item" to="/">
                  Home
                </LinkScaleAnimation>
                <LinkScaleAnimation className="navbar-item" to="/main">
                  Upload
                </LinkScaleAnimation>
                <LinkScaleAnimation
                  className="navbar-item"
                  to="/upload-history"
                >
                  History
                </LinkScaleAnimation>
              </div>
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
      </div>

      <div className="hamburger" onClick={toggleMobileMenu}>
        {isMobileMenuOpen ? "✖" : "☰"}
      </div>

      {isMobileMenuOpen && (
        <div className="mobile-menu">
          {isLandingPage && !user ? (
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
          ) : (
            !isLoginPage &&
            !isRegisterPage && (
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
                <Link
                  className="mobile-menu-item"
                  to="/"
                  onClick={handleLogout}
                >
                  Logout
                </Link>
              </>
            )
          )}
        </div>
      )}
    </div>
  );
}

export default Navbar;
