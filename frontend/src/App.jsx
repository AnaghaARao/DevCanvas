import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Upload from "./pages/Upload";
import NotFound from "./pages/NotFound";
import About from "./pages/About";
import Services from "./pages/Services";
import Contact from "./pages/Contact";
import PrivacyPolicy from "./pages/PrivacyPolicy";
import TermsOfServices from "./pages/TermsOfServices";
import ProtectedRoute from "./components/ProtectedRoutes";
import LandingPage from "./pages/LandingPage";
import Navbar from "./components/Navbar";
import "./styles/general.css";
import ActivateAccount from "./pages/ActivateAccount";
import OutputPage from "./pages/OutputPage";
import History from "./pages/History";
import { AnimatePresence } from "framer-motion";

function Logout() {
  localStorage.clear();
  return <Navigate to="/login" />;
}

function RegisterAndLogout() {
  localStorage.clear();
  return <Register />;
}

function App() {
  return (
    <div className="maindiv">
      <BrowserRouter>
        <Navbar />
        <AnimatePresence mode="wait">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route
              path="/main"
              element={
                <ProtectedRoute>
                  <Upload />
                </ProtectedRoute>
              }
            />
            <Route
              path="/upload-history"
              element={
                <ProtectedRoute>
                  <History />
                </ProtectedRoute>
              }
            />
            <Route
              path="/documentation"
              element={
                <ProtectedRoute>
                  <OutputPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/authentication/activate/:uidb64/:token"
              element={<ActivateAccount />}
            />
            <Route path="/authentication/login/" element={<Login />} />
            <Route path="/authentication/register/" element={<Register />} />
            <Route path="/authentication/logout/" element={<Logout />} />
            <Route path="/about" element={<About />} />
            <Route path="/services/" element={<Services />} />
            {/* <Route path="/contact/" element={<Contact />} /> */}
            <Route path="/privacy-policy/" element={<PrivacyPolicy />} />
            <Route path="/terms-of-service/" element={<TermsOfServices />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </AnimatePresence>
      </BrowserRouter>
    </div>
  );
}

export default App;
