import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { useEffect, useState } from "react";

function ActivateAccount() {
  const base_url = import.meta.env.VITE_API_URL;
  const { uidb64, token } = useParams();
  const navigate = useNavigate();
  const [activationMessage, setActivationMessage] = useState("");

  useEffect(() => {
    const verifyAccount = async () => {
      try {
        const response = await axios.get(
          `${base_url}/authentication/activate/${uidb64}/${token}/`
        );
        setActivationMessage(response.data.message);
        alert(response.data.message);
        navigate("/authentication/login");
      } catch (error) {
        const errorMessage = error.response?.data?.error || "Activation failed";
        setActivationMessage(errorMessage);
        alert(errorMessage);
      }
    };

    if (uidb64 && token) {
      verifyAccount();
    } else {
      alert("Invalid activation link.");
      navigate("/authentication/login");
    }
  }, [uidb64, token, navigate]);

  return (
    <div>
      <h2>Account Activation</h2>
      <p>{activationMessage}</p>
    </div>
  );
}

export default ActivateAccount;
