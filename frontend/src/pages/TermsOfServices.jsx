import React from "react";
import "../styles/extraPages.css";
import intro from "/intropic.png";
import Footer from "../components/Footer.jsx";

const TermsOfServices = () => {
  return (
    <section>
      <div className="page-container terms-of-service">
        <h1 className="main-heading">Terms of Service</h1>
        <hr className="divider" />
        <div className="img-container">
          <div className="flex-content">
            <p>
              By accessing or using our platform, you agree to be bound by these
              Terms of Service.
              <br /> Please read them carefully.
            </p>
            <div>
              <h2>Account Responsibilities</h2>
              <p>
                Users are responsible for maintaining the confidentiality of
                their accounts. Any activity conducted through your account is
                your responsibility.
              </p>
            </div>
            <div>
              <h2>Acceptable Use</h2>
              <p>
                You agree not to use our platform for any unlawful or harmful
                activities. We reserve the right to terminate access if a user
                violates these terms.
              </p>
            </div>
            <div>
              <h2>Service Availability</h2>
              <p>
                While we strive to maintain a reliable platform, we may need to
                suspend or terminate services from time to time for maintenance
                or updates.
              </p>
            </div>
            <div>
              <h2>Limitation of Liability</h2>
              <p>
                We are not liable for any damages arising from the use or
                inability to use our services, except as required by law.
              </p>
            </div>
          </div>
          <img src={intro} alt="Graphic Image" />
        </div>
        <hr className="divider" />
      </div>
      <Footer />
    </section>
  );
};

export default TermsOfServices;
