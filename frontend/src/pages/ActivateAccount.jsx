import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { useEffect, useState } from "react";

function ActivateAccount() {
  const { uidb64, token } = useParams(); // Extract uidb64 and token from URL
  const navigate = useNavigate();
  const [activationMessage, setActivationMessage] = useState("");

  useEffect(() => {
    // Send request to the backend with uidb64 and token
    axios
      .get(`/activate/${uidb64}/${token}`)
      .then((response) => {
        // Handle success response
        setActivationMessage(response.data.message);
        navigate("/authentication/login"); // Redirect to login page after successful activation
      })
      .catch((error) => {
        // Handle error response
        setActivationMessage(error.response.data.error || "Activation failed");
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
