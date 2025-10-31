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
    <div
      style={{
        height: "100vh",
        width: "100%",
        background:
          "radial-gradient(circle at 10% 20%, #2b2d77, #15172b 70%)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        fontFamily: "'Poppins', sans-serif",
      }}
    >
      {/* Glass Login Card */}
      <form
        onSubmit={handleLogin}
        style={{
          width: "350px",
          padding: "40px 30px",
          borderRadius: "16px",
          background: "rgba(255, 255, 255, 0.1)",
          boxShadow: "0 8px 32px rgba(31, 38, 135, 0.37)",
          backdropFilter: "blur(12px)",
          WebkitBackdropFilter: "blur(12px)",
          border: "1px solid rgba(255, 255, 255, 0.18)",
          color: "#fff",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        {/* Avatar Circle */}
        <div
          style={{
            width: "80px",
            height: "80px",
            borderRadius: "50%",
            background: "rgba(255,255,255,0.2)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "40px",
            marginBottom: "20px",
          }}
        >
          👤
        </div>

        <h2 style={{ marginBottom: "25px", fontWeight: "500" }}>Welcome Back</h2>

        <input
          type="email"
          placeholder="Email ID"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={{
            width: "100%",
            padding: "12px",
            marginBottom: "15px",
            borderRadius: "8px",
            border: "none",
            outline: "none",
            background: "rgba(255, 255, 255, 0.15)",
            color: "#fff",
            fontSize: "14px",
          }}
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
            marginBottom: "10px",
            borderRadius: "8px",
            border: "none",
            outline: "none",
            background: "rgba(255, 255, 255, 0.15)",
            color: "#fff",
            fontSize: "14px",
          }}
        />

        <div
          style={{
            width: "100%",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            fontSize: "13px",
            marginBottom: "20px",
            color: "rgba(255,255,255,0.7)",
          }}
        >
          <label>
            <input type="checkbox" style={{ marginRight: "5px" }} /> Remember me
          </label>
          <span
            style={{
              textDecoration: "underline",
              cursor: "pointer",
            }}
          >
            Forgot password?
          </span>
        </div>

        <button
          type="submit"
          style={{
            width: "100%",
            padding: "12px",
            borderRadius: "8px",
            border: "none",
            background:
              "linear-gradient(90deg, rgba(99,102,241,1) 0%, rgba(168,85,247,1) 100%)",
            color: "#fff",
            fontWeight: "600",
            fontSize: "15px",
            cursor: "pointer",
            transition: "0.3s",
          }}
          onMouseOver={(e) => (e.target.style.opacity = "0.85")}
          onMouseOut={(e) => (e.target.style.opacity = "1")}
        >
          LOGIN
        </button>

        {message && (
          <p
            style={{
              marginTop: "15px",
              textAlign: "center",
              color: "#ff8a8a",
              fontSize: "13px",
            }}
          >
            {message}
          </p>
        )}
      </form>
    </div>
  );
}
