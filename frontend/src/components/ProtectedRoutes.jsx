import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { ACCESS_TOKEN } from "../constants";

function ProtectedRoute() {
  const isAuthenticated = !!localStorage.getItem(ACCESS_TOKEN);

  return isAuthenticated ? <Outlet /> : <Navigate to="/authentication/login" />;
}

export default ProtectedRoute;
