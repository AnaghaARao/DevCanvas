import React from "react";
import Form from "../components/Form";

function Login() {
  //   return <Form route="/api/token/" method="login"></Form>;
  return <Form route="/authentication/login" method="login" />;
}

export default Login;