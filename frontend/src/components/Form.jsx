import { useState, useEffect } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import "../styles/general.css";
import "../styles/form.css";
import { useValidation } from "../hooks/useValidation";
import PersonIcon from "@mui/icons-material/Person";
import LockIcon from "@mui/icons-material/Lock";
import EmailIcon from "@mui/icons-material/Email";
import CheckCircleSharpIcon from "@mui/icons-material/CheckCircleSharp";
import CancelSharpIcon from "@mui/icons-material/CancelSharp";
import VisibilitySharpIcon from "@mui/icons-material/VisibilitySharp";
import VisibilityOffSharpIcon from "@mui/icons-material/VisibilityOffSharp";

function Form({ route, method }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const name = method === "login" ? "Sign In" : "Sign Up";
  const { errors, successMessages, validateUsername, validateEmail } =
    useValidation();
  const [passwordError, setPasswordError] = useState(null);

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
      alert("Please fix the validation errors before submitting.");
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
        if (res.data.access && res.data.refresh) {
          localStorage.setItem(ACCESS_TOKEN, res.data.access);
          localStorage.setItem(REFRESH_TOKEN, res.data.refresh);
          console.log("Access Token:", localStorage.getItem(ACCESS_TOKEN));
          console.log("Refresh Token:", localStorage.getItem(REFRESH_TOKEN));
          alert(`Welcome ${username}, you are now logged in`);
          navigate("/main");
        } else if (res.data.message) {
          alert(res.data.message);
        }
      } else {
        alert(res.data.message);
        console.log(res.data.message);
        navigate("/main");
      }
    } catch (error) {
      if (error.response) {
        const { status, data } = error.response;

        if (status === 400 || status === 403 || status === 409) {
          const messages = Object.values(data).flat();
          messages.forEach((msg) => alert(msg));
        } else if (status === 500) {
          alert("An internal server error occurred. Please try again later.");
        } else {
          alert("An unexpected error occurred. Please try again.");
        }
      } else {
        alert(
          "Unable to connect to the server. Please check your internet connection and try again."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-info">
        <h2 className="form-name">{name}</h2>
        {method === "register" && (
          <p className="form-desc">Welcome! Let's get you started.</p>
        )}
        {method === "login" && (
          <p className="form-desc">Welcome back, you've been missed!</p>
        )}
      </div>

      <div className="form-container">
        <div className="input-div">
          <PersonIcon />
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
              <CancelSharpIcon />
            </span>
          )}

          {successMessages.username && (
            <span title={successMessages.username}>
              <CheckCircleSharpIcon />
            </span>
          )}
        </div>

        {method === "register" && (
          <div className="input-div">
            <EmailIcon />
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
                <CancelSharpIcon />
              </span>
            )}
            {successMessages.email && (
              <span title={successMessages.email}>
                <CheckCircleSharpIcon />
              </span>
            )}
          </div>
        )}
        <div className="input-div">
          <LockIcon />
          <input
            className={`${passwordError ? "input-error" : ""}`}
            type={showPassword ? "text" : "password"} // Toggle between "text" and "password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            required
          />
          <span
            onClick={togglePasswordVisibility}
            style={{ cursor: "pointer" }}
          >
            {showPassword ? (
              <VisibilityOffSharpIcon style={{ color: "red" }} />
            ) : (
              <VisibilitySharpIcon style={{ color: "red" }} />
            )}
          </span>
        </div>

        <button className="btn form-button" type="submit" disabled={loading}>
          {loading ? "Processing..." : name}
        </button>
      </div>
    </form>
  );
}

export default Form;
