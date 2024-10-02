import { useState, useEffect } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import "../styles/general.css";
import "../styles/form.css";
import { useValidation } from "../hooks/useValidation";
import { toast } from "react-toastify";

function Form({ route, method }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const name = method === "login" ? "Sign In" : "Sign Up";
  const { errors, successMessages, validateUsername, validateEmail } =
    useValidation();
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
      toast.error("Please fix the validation errors before submitting.");
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
          toast.success(`Welcome ${username}, you are now logged in`);
          navigate("/");
        } else if (res.data.message) {
          toast.info(res.data.message);
        }
      } else {
        toast.success(res.data.message);
        navigate("/authentication/login/");
      }
    } catch (error) {
      if (error.response) {
        const { status, data } = error.response;

        if (status === 400) {
          const messages = Object.values(data).flat();
          messages.forEach((msg) => toast.error(msg));
        } else if (status === 409) {
          const messages = Object.values(data).flat();
          messages.forEach((msg) => toast.error(msg));
        } else if (status === 500) {
          toast.error(
            "An internal server error occurred. Please try again later."
          );
        } else {
          toast.error("An unexpected error occurred. Please try again.");
        }
      } else {
        toast.error(
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
        <input
          className={`form-input ${
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
          <span className="error-text">{errors.username}</span>
        )}
        {successMessages.username && (
          <span className="success-text">{successMessages.username}</span>
        )}

        {method === "register" && (
          <>
            <input
              className={`form-input ${
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
            {errors.email && <span className="error-text">{errors.email}</span>}
            {successMessages.email && (
              <span className="success-text">{successMessages.email}</span>
            )}
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

        <button className="btn form-button" type="submit" disabled={loading}>
          {loading ? "Processing..." : name}
        </button>
      </div>
    </form>
  );
}

export default Form;
