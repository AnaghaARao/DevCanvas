import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { useEffect, useState } from "react";

function ActivateAccount() {
  const { uidb64, token } = useParams();
  const navigate = useNavigate();
  const [activationMessage, setActivationMessage] = useState("");

  useEffect(() => {
    axios
      .get(`${BACKEND_URL}/activate/${uidb64}/${token}/`)
      .then((response) => {
        setActivationMessage(response.data.message);
<<<<<<< HEAD
        navigate("/authentication/login"); // Redirect to login page after successful activation
=======
        alert(response.data.message);
        navigate("/authentication/login");
>>>>>>> 5a6c1ae8c0423e92cf950e7c207d13586d7fd08e
      })
      .catch((error) => {
        setActivationMessage(
          error.response?.data?.error || "Activation failed"
        );
        alert(error.response?.data?.error || "Activation failed");
      });
  }, [uidb64, token, navigate]);

  return (
    <div>
      <h2>Account Activation</h2>
      <p>{activationMessage}</p>
    </div>
  );
}

export default ActivateAccount;
