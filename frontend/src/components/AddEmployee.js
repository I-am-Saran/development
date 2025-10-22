import { useState, useEffect, useRef } from "react";
import { PDFDocument } from "pdf-lib";

export default function AddEmployee() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [position, setPosition] = useState("");
  const [file, setFile] = useState(null);
  const [compressedFile, setCompressedFile] = useState(null);
  const [message, setMessage] = useState("");
  const [employees, setEmployees] = useState([]);
  const fileInputRef = useRef();
  const compressedInputRef = useRef();

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      const res = await fetch("https://development-p6rb.onrender.com/employees");
      const data = await res.json();
      if (data.employees) setEmployees(data.employees);
    } catch (err) {
      console.error("Failed to fetch employees:", err);
    }
  };

  // Compress PDF file
  const handleCompressedUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.type !== "application/pdf") {
      alert("Please upload only PDF files");
      return;
    }

    try {
      const arrayBuffer = await file.arrayBuffer();
      const pdfDoc = await PDFDocument.load(arrayBuffer);
      const compressedBytes = await pdfDoc.save({ useObjectStreams: true });
      const newFile = new File([compressedBytes], `compressed_${file.name}`, {
        type: "application/pdf",
      });
      setCompressedFile(newFile);
      alert("✅ PDF compressed successfully!");
    } catch (error) {
      console.error("Error compressing PDF:", error);
      alert("❌ Failed to compress PDF");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append("name", name);
    formData.append("email", email);
    formData.append("position", position);
    if (file) formData.append("file", file);
    if (compressedFile) formData.append("compressed_file", compressedFile); // match backend

    try {
      const res = await fetch("https://development-p6rb.onrender.com/add-employee", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setMessage(data.message || data.error || "Uploaded successfully!");

      // reset form
      setName("");
      setEmail("");
      setPosition("");
      setFile(null);
      setCompressedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      if (compressedInputRef.current) compressedInputRef.current.value = "";

      fetchEmployees();
    } catch (err) {
      console.error(err);
      setMessage("Something went wrong!");
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>Add Employee</h2>

      <form onSubmit={handleSubmit} style={styles.form}>
        <input
          type="text"
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          style={styles.input}
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={styles.input}
        />
        <input
          type="text"
          placeholder="Position"
          value={position}
          onChange={(e) => setPosition(e.target.value)}
          required
          style={styles.input}
        />

        {/* Normal Upload */}
        <div
          style={{
            background: "#f9fafb",
            padding: "16px",
            borderRadius: "12px",
            boxShadow: "0 2px 6px rgba(0,0,0,0.08)",
            marginBottom: "16px",
            transition: "all 0.3s ease",
          }}
        >
          <label
            style={{
              display: "block",
              fontWeight: "600",
              fontSize: "14px",
              color: "#1f2937",
              marginBottom: "8px",
            }}
          >
            Upload Normal PDF:
          </label>
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files[0])}
            ref={fileInputRef}
            style={{
              width: "100%",
              padding: "10px",
              border: "2px dashed #9ca3af",
              borderRadius: "10px",
              background: "#fff",
              cursor: "pointer",
              transition: "border-color 0.3s ease, background 0.3s ease",
            }}
            onMouseOver={(e) => {
              e.target.style.borderColor = "#2563eb";
              e.target.style.background = "#f0f9ff";
            }}
            onMouseOut={(e) => {
              e.target.style.borderColor = "#9ca3af";
              e.target.style.background = "#fff";
            }}
          />
        </div>

        {/* Compressed Upload */}
        <div
  style={{
    background: "#f9fafb",
    padding: "16px",
    borderRadius: "12px",
    boxShadow: "0 2px 6px rgba(0,0,0,0.08)",
    transition: "all 0.3s ease",
  }}
>
  <label
    style={{
      display: "block",
      fontWeight: "600",
      fontSize: "14px",
      color: "#1f2937",
      marginBottom: "8px",
    }}
  >
    Upload & Compress PDF:
  </label>
  <input
    type="file"
    accept="application/pdf"
    onChange={handleCompressedUpload}
    ref={compressedInputRef}
    style={{
      width: "100%",
      padding: "10px",
      border: "2px dashed #9ca3af",
      borderRadius: "10px",
      background: "#fff",
      cursor: "pointer",
      transition: "border-color 0.3s ease, background 0.3s ease",
    }}
    onMouseOver={(e) => {
      e.target.style.borderColor = "#2563eb";
      e.target.style.background = "#f0f9ff";
    }}
    onMouseOut={(e) => {
      e.target.style.borderColor = "#9ca3af";
      e.target.style.background = "#fff";
    }}
  />
</div>

        <button type="submit" style={styles.button}>
          Add Employee
        </button>
      </form>

      {message && <p style={styles.message}>{message}</p>}

      <h3 style={styles.tableHeading}>Employee List</h3>
      <div style={styles.tableContainer}>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Name</th>
              <th style={styles.th}>Email</th>
              <th style={styles.th}>Position</th>
              <th style={styles.th}>File</th>
              <th style={styles.th}>Compressed File</th>
            </tr>
          </thead>
          <tbody>
            {employees.map((emp) => (
              <tr key={emp.id} style={styles.tr}>
                <td style={styles.td}>{emp.name}</td>
                <td style={styles.td}>{emp.email}</td>
                <td style={styles.td}>{emp.position}</td>
                <td style={styles.td}>
                  {emp.file_url ? (
                    <a href={emp.file_url} target="_blank" rel="noopener noreferrer" style={styles.link}>
                      View File
                    </a>
                  ) : (
                    "No File"
                  )}
                </td>
                <td style={styles.td}>
                  {emp.compressed_file_url ? (
                    <a href={emp.compressed_file_url} target="_blank" rel="noopener noreferrer" style={styles.link}>
                      View File
                    </a>
                  ) : (
                    "No File"
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
// Styles
const styles = {
  container: {
    maxWidth: "900px",
    margin: "50px auto",
    padding: "20px",
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    backgroundColor: "#f9f9f9",
    borderRadius: "10px",
    boxShadow: "0px 0px 15px rgba(0,0,0,0.1)",
  },
  heading: {
    textAlign: "center",
    marginBottom: "20px",
    color: "#333",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "15px",
    marginBottom: "30px",
  },
  input: {
    padding: "10px",
    borderRadius: "5px",
    border: "1px solid #ccc",
    fontSize: "16px",
  },
  fileInput: {
    fontSize: "16px",
  },
  button: {
    padding: "12px",
    backgroundColor: "#08f300ff",
    color: "#fff",
    border: "none",
    borderRadius: "5px",
    fontSize: "16px",
    cursor: "pointer",
    transition: "background-color 0.3s",
  },
  message: {
    color: "green",
    fontWeight: "bold",
    marginTop: "10px",
    textAlign: "center",
  },
  tableHeading: {
    marginBottom: "10px",
    color: "#333",
  },
  tableContainer: {
    overflowX: "auto",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
  },
  th: {
    textAlign: "left",
    padding: "10px",
    backgroundColor: "#0070f3",
    color: "#fff",
  },
  td: {
    padding: "10px",
    borderBottom: "1px solid #ccc",
  },
  tr: {
    transition: "background-color 0.2s",
  },
  link: {
    color: "#0070f3",
    textDecoration: "none",
    fontWeight: "bold",
  },
};