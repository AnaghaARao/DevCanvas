import React from "react";
import { Navigate } from "react-router-dom";
import { ACCESS_TOKEN } from "../constants";

function ProtectedRoute({ children }) {
  const isAuthenticated = localStorage.getItem(ACCESS_TOKEN);

  return isAuthenticated ? children : <Navigate to="/authentication/login" />;
}

export default ProtectedRoute;
