// src/hooks/useValidation.js
import { useState, useCallback } from "react";
import api from "../api";

export function useValidation() {
  const [errors, setErrors] = useState({});
  const [successMessages, setSuccessMessages] = useState({});

  const validateUsername = useCallback(async (username) => {
    try {
      const res = await api.post(`/authentication/validate-username/`, {
        username,
      });
      if (res.data.username_error) {
        setErrors((prev) => ({
          ...prev,
          username: res.data.username_error,
        }));
        setSuccessMessages((prev) => ({ ...prev, username: null }));
      } else if (res.data.username_valid) {
        setErrors((prev) => ({ ...prev, username: null }));
        setSuccessMessages((prev) => ({
          ...prev,
          username: "Username is available!",
        }));
      }
    } catch (error) {
      if (error.response && error.response.status === 409) {
        setErrors((prev) => ({
          ...prev,
          username: "Sorry! Username is already in use. Please choose another.",
        }));
        setSuccessMessages((prev) => ({ ...prev, username: null }));
      } else {
        setErrors((prev) => ({
          ...prev,
          username: "Error validating username.",
        }));
        setSuccessMessages((prev) => ({ ...prev, username: null }));
      }
    }
  }, []);

  const validateEmail = useCallback(async (email) => {
    try {
      const res = await api.post(`/authentication/validate-email/`, { email });
      if (res.data.email_error) {
        setErrors((prev) => ({ ...prev, email: res.data.email_error }));
        setSuccessMessages((prev) => ({ ...prev, email: null }));
      } else if (res.data.email_valid) {
        setErrors((prev) => ({ ...prev, email: null }));
        setSuccessMessages((prev) => ({
          ...prev,
          email: "Email is available!",
        }));
      }
    } catch (error) {
      if (error.response && error.response.status === 409) {
        setErrors((prev) => ({
          ...prev,
          email: "Sorry! Email is already in use. Please choose another.",
        }));
        setSuccessMessages((prev) => ({ ...prev, email: null }));
      } else {
        setErrors((prev) => ({ ...prev, email: "Error validating email." }));
        setSuccessMessages((prev) => ({ ...prev, email: null }));
      }
    }
  }, []);

  return { errors, successMessages, validateUsername, validateEmail };
}
