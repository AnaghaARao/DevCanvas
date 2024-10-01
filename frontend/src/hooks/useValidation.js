import { useState, useCallback } from "react";
import api from "../api";

export function useValidation() {
  const [errors, setErrors] = useState({});

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
      } else if (res.data.username_valid) {
        setErrors((prev) => ({ ...prev, username: null }));
      }
    } catch (error) {
      setErrors((prev) => ({
        ...prev,
        username: "Error validating username.",
      }));
    }
  }, []);

  const validateEmail = useCallback(async (email) => {
    try {
      const res = await api.post(`/authentication/validate-email/`, { email });
      if (res.data.email_error) {
        setErrors((prev) => ({ ...prev, email: res.data.email_error }));
      } else if (res.data.email_valid) {
        setErrors((prev) => ({ ...prev, email: null }));
      }
    } catch (error) {
      setErrors((prev) => ({ ...prev, email: "Error validating email." }));
    }
  }, []);

  return { errors, validateUsername, validateEmail };
}
