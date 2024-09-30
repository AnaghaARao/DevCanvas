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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    if (errors.username || (method === "register" && errors.email)) {
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
        localStorage.setItem(ACCESS_TOKEN, res.data.access);
        localStorage.setItem(REFRESH_TOKEN, res.data.refresh);
        navigate("/");
      } else {
        navigate("/authentication/login/");
      }
    } catch (error) {
      if (error.response && error.response.data) {
        const messages = Object.values(error.response.data).flat();
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
        className="form-input"
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
