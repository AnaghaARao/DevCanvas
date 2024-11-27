import React from "react";
import "../styles/extraPages.css";
import Footer from "../components/Footer.jsx";

const PrivacyPolicy = () => {
  return (
    <section>
      <div className="page-container privacy-policy">
        <h1 className="main-heading">Privacy Policy</h1>
        <hr className="divider" />
        <p>
          Your privacy is important to us. This Privacy Policy outlines the
          types of information we collect, how we use it, and the measures we
          take to protect your information.
        </p>
        <div>
          <h2>Information Collection</h2>
          <p>
            We collect information that you provide directly to us, such as your
            name, email address, and other contact details. Additionally, we may
            collect usage data when you interact with our platform.
          </p>
        </div>
        <div>
          <h2>Use of Information</h2>
          <p>
            The information we collect helps us improve our services, respond to
            your inquiries, and send you updates about our platform. We never
            share your data with third parties without your consent.
          </p>
        </div>
        <div>
          <h2>Data Security</h2>
          <p>
            We implement robust security measures to protect your personal
            information from unauthorized access or disclosure.
          </p>
        </div>
        <hr className="divider" />
      </div>
      <Footer />
    </section>
  );
};

export default PrivacyPolicy;
