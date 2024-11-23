import { useState, useEffect } from "react";
import api from "../api";
import { motion } from "framer-motion";
import { useNavigate, Link, Navigate } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import { useDispatch } from "react-redux";
import { setUser } from "../store/actions";
import { useValidation } from "../hooks/useValidation";
import PersonIcon from "@mui/icons-material/Person";
import LockIcon from "@mui/icons-material/Lock";
import EmailIcon from "@mui/icons-material/Email";
import CheckCircleSharpIcon from "@mui/icons-material/CheckCircleSharp";
import CancelSharpIcon from "@mui/icons-material/CancelSharp";
import VisibilitySharpIcon from "@mui/icons-material/VisibilitySharp";
import VisibilityOffSharpIcon from "@mui/icons-material/VisibilityOffSharp";
import { ToastContainer, Zoom } from "react-toastify";

import { showAlert, showError, showSuccess } from "../hooks/toastUtils.js";
import "../styles/general.css";
import "../styles/form.css";

function Form({ route, method }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [passwordError, setPasswordError] = useState(null);

  const navigate = useNavigate();
  const dispatch = useDispatch();

  const name = method === "login" ? "Sign In" : "Sign Up";
  const { errors, successMessages, validateUsername, validateEmail } =
    useValidation();

  useEffect(() => {
    if (method === "register" && username) {
      const delayDebounceFn = setTimeout(() => {
        validateUsername(username);
      }, 500);

      return () => clearTimeout(delayDebounceFn);
    }
  }, [username, validateUsername, method]);

  useEffect(() => {
    if (method === "register" && email) {
      const delayDebounceFn = setTimeout(() => {
        validateEmail(email);
      }, 500);

      return () => clearTimeout(delayDebounceFn);
    }
  }, [email, method, validateEmail]);

  const togglePasswordVisibility = () => {
    setShowPassword((prevShowPassword) => !prevShowPassword);
  };

  const validatePassword = (password) => {
    const errors = [];
    if (password.length < 8) {
      errors.push("Password must be at least 8 characters long.");
    }
    if (!/\d/.test(password)) {
      errors.push("Password must contain at least one number.");
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      errors.push("Password must contain at least one special character.");
    }
    return errors.length > 0 ? errors.join(" ") : null;
  };

  useEffect(() => {
    if (password) {
      const error = validatePassword(password);
      setPasswordError(error);
    } else {
      setPasswordError(null);
    }
  }, [password]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    if (
      (method === "register" && (errors.username || errors.email)) ||
      passwordError
    ) {
      showError("Please fix the validation errors before submitting.");
      setLoading(false);
      return;
    }

    const data =
      method === "login"
        ? { username, password }
        : { username, password, email };

    try {
      const res = await api.post(route, data);

      if (method === "login") {
        // login logic
        if (res.data.access && res.data.refresh) {
          localStorage.setItem(ACCESS_TOKEN, res.data.access);
          localStorage.setItem(REFRESH_TOKEN, res.data.refresh);

          dispatch(setUser(username));
          showSuccess(`Welcome ${username}, you are now logged in`);
          navigate("/main");
        } else if (res.data.message) {
          showSuccess(res.data.message);
        }
      } else if (method === "register") {
        // Register logic
        localStorage.setItem("activationPending", "true");
        localStorage.setItem("pendingVerification", true);
        showSuccess(res.data.message);
        console.log(res.data.message);
      }
    } catch (error) {
      if (error.response) {
        const { status, data } = error.response;

        if (status === 400 || status === 403 || status === 409) {
          const messages = Object.values(data).flat();
          messages.forEach((msg) => showError(msg));
        } else if (status === 500) {
          showError(
            "An internal server error occurred. Please try again later."
          );
        } else {
          showError("An unexpected error occurred. Please try again.");
        }
      } else {
        showError(
          "Unable to connect to the server. Please check your internet connection and try again."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <motion.div
        className="form-info"
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <h2 className="form-name">{name}</h2>
        {method === "register" && (
          <p className="form-desc">Welcome! Let's get you started.</p>
        )}
        {method === "login" && (
          <p className="form-desc">Welcome back, you've been missed!</p>
        )}
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3, delay: 0.3 }}
        className="form-container"
      >
        <div className="input-div">
          <PersonIcon className="mui-icons" />
          <input
            className={`${
              errors.username
                ? "input-error"
                : successMessages.username
                ? "input-success"
                : ""
            }`}
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Username"
            required
          />

          {errors.username && (
            <span title={errors.username}>
              <CancelSharpIcon className="mui-icons" />
            </span>
          )}

          {successMessages.username && (
            <span title={successMessages.username}>
              <CheckCircleSharpIcon className="mui-icons" />
            </span>
          )}
        </div>

        {method === "register" && (
          <div className="input-div">
            <EmailIcon className="mui-icons" />
            <input
              className={`${
                errors.email
                  ? "input-error"
                  : successMessages.email
                  ? "input-success"
                  : ""
              }`}
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
              required
            />
            {errors.email && (
              <span title={errors.email}>
                <CancelSharpIcon className="mui-icons" />
              </span>
            )}
            {successMessages.email && (
              <span title={successMessages.email}>
                <CheckCircleSharpIcon className="mui-icons" />
              </span>
            )}
          </div>
        )}
        <div className="input-div">
          <LockIcon className="mui-icons" />
          <input
            className={`${passwordError ? "input-error" : ""}`}
            type={showPassword ? "text" : "password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            required
          />
          <span
            onClick={togglePasswordVisibility}
            style={{ cursor: "pointer" }}
            title="Toggle password visibility."
          >
            {showPassword ? (
              <VisibilityOffSharpIcon className="mui-icons" />
            ) : (
              <VisibilitySharpIcon className="mui-icons" />
            )}
          </span>
        </div>

        <button className="btn form-button" type="submit" disabled={loading}>
          {loading ? "Processing..." : name}
        </button>
        {method === "login" ? (
          <p className="switch-page">
            Don’t have an account?{" "}
            <Link to="/authentication/register" className="switch-link">
              Sign Up
            </Link>
          </p>
        ) : (
          <p className="switch-page">
            Already have an account?{" "}
            <Link to="/authentication/login" className="switch-link">
              Sign In
            </Link>
          </p>
        )}
      </motion.div>
      <ToastContainer
        position="top-right"
        autoClose={5000}
        transition={Zoom}
        closeOnClick={true}
        limit={2}
        theme="dark"
        toastStyle={{
          backgroundColor: "#161616",
        }}
        style={{
          backgroundColor: "transparent",
        }}
      />
    </form>
  );
}

export default Form;
