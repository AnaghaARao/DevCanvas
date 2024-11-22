import { React, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Upload from "./pages/Upload";
import NotFound from "./pages/NotFound";
import ProtectedRoute from "./components/ProtectedRoutes";
import LandingPage from "./pages/LandingPage";
import Navbar from "./components/Navbar";
import "./styles/general.css";
import "./styles/landing.css";
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
  useEffect(() => {
    const handleBeforeUnload = () => {
      localStorage.removeItem("user");
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    };

    window.addEventListener("beforeunload", handleBeforeUnload);

    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, []);
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
            <Route path="*" element={<NotFound />} />
          </Routes>{" "}
        </AnimatePresence>
      </BrowserRouter>
    </div>
  );
}

export default App;
