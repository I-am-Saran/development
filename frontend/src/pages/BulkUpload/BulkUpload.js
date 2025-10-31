import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function BulkUpload() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (
      selectedFile &&
      selectedFile.type ===
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ) {
      setFile(selectedFile);
    } else {
      alert("Please upload a valid Excel file (.xlsx).");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return alert("Please select a file first!");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(
        "https://development-p6rb.onrender.com/bulk_upload",
        {
          method: "POST",
          body: formData,
        }
      );
      const data = await res.json();
      setMessage(data.message || "✅ Upload successful!");
    } catch (error) {
      console.error(error);
      setMessage("❌ Something went wrong!");
    }
  };

  return (
    <div
      style={{
        height: "100vh",
        width: "100%",
        display: "flex",
        background: "radial-gradient(circle at 10% 20%, #2b2d77, #15172b 70%)",
        fontFamily: "'Poppins', sans-serif",
      }}
    >
      {/* Sidebar */}
      <div
        style={{
          width: "220px",
          background: "rgba(255,255,255,0.1)",
          backdropFilter: "blur(10px)",
          borderRight: "1px solid rgba(255,255,255,0.2)",
          display: "flex",
          flexDirection: "column",
          padding: "30px 20px",
          color: "#fff",
        }}
      >
        <h3
          style={{
            marginBottom: "30px",
            textAlign: "center",
            fontWeight: "600",
            fontSize: "18px",
          }}
        >
          Employee Portal
        </h3>

        <button
          onClick={() => navigate("/add-employee")}
          style={menuButton("/add-employee")}
        >
          Add Employee
        </button>

        <button
          onClick={() => navigate("/bulk-upload")}
          style={menuButton("/bulk-upload")}
        >
          Bulk Upload
        </button>

        <button
          onClick={() => {
            localStorage.clear();
            window.location.href = "/";
          }}
          style={{
            marginTop: "auto",
            background: "rgba(255, 77, 77, 0.2)",
            border: "1px solid rgba(255,77,77,0.5)",
            color: "#ffbaba",
            borderRadius: "8px",
            padding: "10px",
            cursor: "pointer",
          }}
        >
          Logout
        </button>
      </div>

      {/* Main Content */}
      <div
        style={{
          flex: 1,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <form
          onSubmit={handleSubmit}
          style={{
            width: "400px",
            padding: "40px",
            borderRadius: "16px",
            background: "rgba(255, 255, 255, 0.1)",
            boxShadow: "0 8px 32px rgba(31, 38, 135, 0.37)",
            backdropFilter: "blur(12px)",
            border: "1px solid rgba(255, 255, 255, 0.18)",
            color: "#fff",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <h2 style={{ marginBottom: "25px", fontWeight: "500" }}>
            Bulk Upload Excel
          </h2>

          <input
            type="file"
            accept=".xlsx"
            onChange={handleFileChange}
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
            Upload
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
    </div>
  );
}

// Helper style for menu buttons
const menuButton = (activePath) => ({
  padding: "10px 12px",
  textAlign: "left",
  border: "none",
  borderRadius: "8px",
  marginBottom: "12px",
  background: "rgba(255,255,255,0.1)",
  color: "#fff",
  cursor: "pointer",
  transition: "0.3s",
  fontWeight: "500",
  fontSize: "14px",
});
