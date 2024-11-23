import React, { useEffect } from "react";
import Form from "../components/Form";
import { useNavigate } from "react-router-dom";

function Register() {
  const navigate = useNavigate();

  useEffect(() => {
    const activationPending = localStorage.setItem("pendingVerification", true);
    if (activationPending) {
      // Redirect to login if user is pending activation
      navigate("/authentication/login");
    }
  }, [navigate]);

  return <Form route="/authentication/register/" method="register" />;
}

export default Register;
