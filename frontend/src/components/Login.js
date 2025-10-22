import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("https://development-p6rb.onrender.com/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (data.message === "Login successful!") {
        navigate("/add-employee");
      } else {
        setMessage(data.message || data.error);
      }
    } catch (err) {
      setMessage("Something went wrong!");
    }
  };

  return (
    <div style={{ maxWidth: "400px", margin: "100px auto", textAlign: "center" }}>
      <h2>Login</h2>
        <form
  onSubmit={handleLogin}
  style={{
    maxWidth: "400px",
    margin: "50px auto",
    padding: "30px",
    borderRadius: "15px",
    boxShadow: "0 10px 25px rgba(0,0,0,0.1)",
    backgroundColor: "#ffffff",
    display: "flex",
    flexDirection: "column",
  }}
>
  <h2 style={{ textAlign: "center", marginBottom: "20px", color: "#333", fontFamily: "Arial, sans-serif" }}>
    Welcome Back 👋
  </h2>

  <input
    type="email"
    placeholder="Email"
    value={email}
    onChange={(e) => setEmail(e.target.value)}
    required
    style={{
      width: "100%",
      padding: "12px",
      marginBottom: "15px",
      borderRadius: "8px",
      border: "1px solid #ccc",
      fontSize: "16px",
      outline: "none",
      transition: "0.3s",
    }}
    onFocus={(e) => (e.target.style.borderColor = "#4F46E5")}
    onBlur={(e) => (e.target.style.borderColor = "#ccc")}
  />

  <input
    type="password"
    placeholder="Password"
    value={password}
    onChange={(e) => setPassword(e.target.value)}
    required
    style={{
      width: "100%",
      padding: "12px",
      marginBottom: "20px",
      borderRadius: "8px",
      border: "1px solid #ccc",
      fontSize: "16px",
      outline: "none",
      transition: "0.3s",
    }}
    onFocus={(e) => (e.target.style.borderColor = "#4F46E5")}
    onBlur={(e) => (e.target.style.borderColor = "#ccc")}
  />

  <button
    type="submit"
    style={{
      width: "100%",
      padding: "12px",
      borderRadius: "8px",
      background: "linear-gradient(90deg, #4F46E5, #6D28D9)",
      color: "#fff",
      fontSize: "16px",
      fontWeight: "bold",
      border: "none",
      cursor: "pointer",
      transition: "0.3s",
    }}
    onMouseOver={(e) => (e.target.style.opacity = "0.85")}
    onMouseOut={(e) => (e.target.style.opacity = "1")}
  >
    Login
  </button>

  
</form>

      {message && <p>{message}</p>}
    </div>
  );
}
