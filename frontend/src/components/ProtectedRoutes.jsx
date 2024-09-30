// import { Navigate } from "react-router-dom";
// import { jwtDecode } from "jwt-decode";
// import api from "../api";
// import { REFRESH_TOKEN } from "../constants";
// import { ACCESS_TOKEN } from "../constants";
// import { useState, useEffect } from "react";

// function ProtectedRoute({ children }) {
//   const [isAuthorized, setIsAuthorized] = useState(null);

//   useEffect(() => {
//     auth().catch(() => setIsAuthorized(false));

//     return () => {
//       second;
//     };
//   }, [third]);

//   const refreshToken = async () => {
//     const refreshToken = localStorage.getItem(REFRESH_TOKEN);
//     try {
//       const res = await api.post("/api/token/refresh/", {
//         refresh: REFRESH_TOKEN,
//       });

//       if (res.status === 200) {
//         localStorage.setItem(ACCESS_TOKEN, res.data.access);
//         setIsAuthorized(true);
//       } else {
//         setIsAuthorized(false);
//       }
//     } catch (error) {
//       console.log(error);
//       setIsAuthorized(false);
//     }
//   };

//   const auth = async () => {
//     const token = localStorage.getItem(ACCESS_TOKEN);
//     if (!token) {
//       setIsAuthorized(false);
//       return;
//     }
//     const decoded = jwtDecode(token);
//     const tokenExpiration = decoded.exp;
//     const now = Date.now() / 1000; // date in seconds

//     if (tokenExpiration < now) {
//       await refreshToken();
//     } else {
//       setIsAuthorized(true);
//     }
//   };

//   if (isAuthorized === null) {
//     return <div>Loading...</div>;
//   }

//   return isAuthorized ? children : <Navigate to="login" />;
// }

// export default ProtectedRoute;

// src/components/ProtectedRoute.jsx

import React from "react";
import { Navigate } from "react-router-dom";
import { ACCESS_TOKEN } from "../constants";

function ProtectedRoute({ children }) {
  const isAuthenticated = !!localStorage.getItem(ACCESS_TOKEN);

  return isAuthenticated ? children : <Navigate to="/authentication/login" />;
}

export default ProtectedRoute;
