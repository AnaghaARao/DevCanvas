import { useState, useCallback } from "react";
import api from "../api";

export function useValidation() {
  const [errors, setErrors] = useState({});

  const validateUsername = useCallback(async (username) => {
    try {
      const res = await api.get(`/authentication/validate-username/`, {
        params: { username },
      });
      if (!res.data.username_valid) {
        setErrors((prev) => ({
          ...prev,
          username: "Username is already taken.",
        }));
      } else {
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
      const res = await api.get(`/authentication/validate-email/`, {
        params: { email },
      });
      if (!res.data.email_valid) {
        setErrors((prev) => ({ ...prev, email: "Email is already in use." }));
      } else {
        setErrors((prev) => ({ ...prev, email: null }));
      }
    } catch (error) {
      setErrors((prev) => ({ ...prev, email: "Error validating email." }));
    }
  }, []);

  return { errors, validateUsername, validateEmail };
}
