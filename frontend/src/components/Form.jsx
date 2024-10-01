import { useState, useEffect } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import "../styles/Form.css";
import { useValidation } from "../hooks/useValidation";

function Form({ route, method }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const name = method === "login" ? "Login" : "Register";
  const { errors, validateUsername, validateEmail } = useValidation();
  const [passwordError, setPasswordError] = useState(null);

  useEffect(() => {
    if (username) {
      const delayDebounceFn = setTimeout(() => {
        validateUsername(username);
      }, 500);

      return () => clearTimeout(delayDebounceFn);
    }
  }, [username, validateUsername]);

  useEffect(() => {
    if (method === "register" && email) {
      const delayDebounceFn = setTimeout(() => {
        validateEmail(email);
      }, 500);

      return () => clearTimeout(delayDebounceFn);
    }
  }, [email, method, validateEmail]);

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
      errors.username ||
      (method === "register" && errors.email) ||
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
          navigate("/");
        } else if (res.data.message) {
          alert(res.data.message);
        }
      } else {
        alert(res.data.message);
        navigate("/authentication/login/");
      }
    } catch (error) {
      if (error.response && error.response.data) {
        const responseData = error.response.data;
        const messages = [];

        // Collect all error messages from the response
        Object.keys(responseData).forEach((key) => {
          if (Array.isArray(responseData[key])) {
            messages.push(...responseData[key]);
          } else if (typeof responseData[key] === "string") {
            messages.push(responseData[key]);
          }
        });

        alert(messages.join("\n"));
      } else {
        alert("An unexpected error occurred. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="form-container">
      <h1>{name}</h1>

      <input
        className={`form-input ${errors.username ? "input-error" : ""}`}
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
        required
      />
      {errors.username && <span className="error-text">{errors.username}</span>}

      {method === "register" && (
        <>
          <input
            className={`form-input ${errors.email ? "input-error" : ""}`}
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            required
          />
          {errors.email && <span className="error-text">{errors.email}</span>}
        </>
      )}

      <input
        className={`form-input ${passwordError ? "input-error" : ""}`}
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
      />

      <button className="form-button" type="submit" disabled={loading}>
        {loading ? "Processing..." : name}
      </button>
    </form>
  );
}

export default Form;
