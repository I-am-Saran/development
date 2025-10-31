import { useState, useEffect, useRef } from "react";
import { PDFDocument } from "pdf-lib";
import { useNavigate } from "react-router-dom";

export default function AddEmployee() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [position, setPosition] = useState("");
  const [file, setFile] = useState(null);
  const [compressedFile, setCompressedFile] = useState(null);
  const [message, setMessage] = useState("");
  const [employees, setEmployees] = useState([]);
  const [bulkFiles, setBulkFiles] = useState([]);
  const fileInputRef = useRef();
  const compressedInputRef = useRef();
  const bulkInputRef = useRef();
  const navigate = useNavigate();

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
  try {
    const res = await fetch("https://development-p6rb.onrender.com/employees");
    const data = await res.json();
    setEmployees(data); // API returns an array directly
  } catch (err) {
    console.error("Failed to fetch employees:", err);
  }
};


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
    if (compressedFile) formData.append("compressed_file", compressedFile);
    if (bulkFiles.length > 0) {
      bulkFiles.forEach((f) => formData.append("bulk_files", f));
    }

    try {
      const res = await fetch("https://development-p6rb.onrender.com/add-employee", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setMessage(data.message || data.error || "Uploaded successfully!");

      setName("");
      setEmail("");
      setPosition("");
      setFile(null);
      setCompressedFile(null);
      setBulkFiles([]);
      if (fileInputRef.current) fileInputRef.current.value = "";
      if (compressedInputRef.current) compressedInputRef.current.value = "";
      if (bulkInputRef.current) bulkInputRef.current.value = "";

      fetchEmployees();
    } catch (err) {
      console.error(err);
      setMessage("Something went wrong!");
    }
  };

  return (
    <div style={styles.layout}>
      {/* Sidebar */}
      <div style={styles.sidebar}>
        <h2 style={styles.logo}>⚙️ Admin Panel</h2>
        <ul style={styles.menu}>
          <li
            style={styles.activeMenuItem}
            onClick={() => navigate("/add-employee")}
          >
            ➕ Add Employee
          </li>
          <li
            style={styles.menuItem}
            onClick={() => navigate("/bulk-upload")}
          >
            📂 Bulk Upload
          </li>
        </ul>
        <button
          style={styles.logoutButton}
          onClick={() => {
            localStorage.clear();
            navigate("/");
          }}
        >
          🚪 Logout
        </button>
      </div>

      {/* Main Content */}
      <div style={styles.mainContent}>
        <h2 style={styles.heading}>Add Employee Form</h2>
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
          <div style={styles.uploadBox}>
            <label style={styles.label}>Upload Normal PDF:</label>
            <input
              type="file"
              accept="application/pdf"
              onChange={(e) => setFile(e.target.files[0])}
              ref={fileInputRef}
              style={styles.fileInput}
            />
          </div>

          {/* Compressed Upload */}
          <div style={styles.uploadBox}>
            <label style={styles.label}>Upload & Compress PDF:</label>
            <input
              type="file"
              accept="application/pdf"
              onChange={handleCompressedUpload}
              ref={compressedInputRef}
              style={styles.fileInput}
            />
          </div>

          {/* Bulk Upload */}
          <div style={styles.uploadBox}>
            <label style={styles.label}>Upload Multiple Files (Bulk Upload):</label>
            <input
              type="file"
              multiple
              accept="application/pdf"
              onChange={(e) => setBulkFiles(Array.from(e.target.files))}
              ref={bulkInputRef}
              style={styles.fileInput}
            />
          </div>

          <button type="submit" style={styles.submitButton}>
            Add Employee
          </button>
        </form>

        {message && <p style={styles.message}>{message}</p>}

        <h3 style={styles.subHeading}>Employee List</h3>
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
                <tr key={emp.id}>
                  <td style={styles.td}>{emp.name}</td>
                  <td style={styles.td}>{emp.email}</td>
                  <td style={styles.td}>{emp.position}</td>
                  <td style={styles.td}>
                    {emp.file_url ? (
                      <a href={emp.file_url} target="_blank" rel="noreferrer" style={styles.link}>
                        View File
                      </a>
                    ) : (
                      "No File"
                    )}
                  </td>
                  <td style={styles.td}>
                    {emp.compressed_file_url ? (
                      <a href={emp.compressed_file_url} target="_blank" rel="noreferrer" style={styles.link}>
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
    </div>
  );
}

// Styles
const styles = {
  layout: {
    display: "flex",
    height: "100vh",
    background: "radial-gradient(circle at 10% 20%, #2b2d77, #15172b 70%)",
    color: "#fff",
    fontFamily: "'Poppins', sans-serif",
  },
  sidebar: {
    width: "220px",
    background: "rgba(255,255,255,0.1)",
    backdropFilter: "blur(12px)",
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
    padding: "20px",
    boxShadow: "4px 0 20px rgba(0,0,0,0.2)",
  },
  logo: {
    fontSize: "18px",
    fontWeight: "600",
    marginBottom: "20px",
  },
  menu: {
    listStyle: "none",
    padding: 0,
  },
  menuItem: {
    padding: "10px 0",
    cursor: "pointer",
    color: "rgba(255,255,255,0.8)",
    transition: "0.3s",
  },
  activeMenuItem: {
    padding: "10px 0",
    fontWeight: "600",
    color: "#fff",
    borderLeft: "4px solid #a855f7",
    paddingLeft: "10px",
  },
  logoutButton: {
    background: "linear-gradient(90deg,#ef4444,#b91c1c)",
    border: "none",
    color: "#fff",
    padding: "10px",
    borderRadius: "8px",
    cursor: "pointer",
    fontWeight: "600",
  },
  mainContent: {
    flex: 1,
    padding: "40px",
    overflowY: "auto",
  },
  heading: {
    fontSize: "24px",
    marginBottom: "30px",
    fontWeight: "500",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "15px",
    width: "350px",
    background: "rgba(255,255,255,0.1)",
    padding: "30px",
    borderRadius: "16px",
    backdropFilter: "blur(12px)",
  },
  input: {
    width: "100%",
    padding: "12px",
    borderRadius: "8px",
    border: "none",
    outline: "none",
    background: "rgba(255,255,255,0.15)",
    color: "#fff",
  },
  uploadBox: {
    display: "flex",
    flexDirection: "column",
    gap: "8px",
  },
  label: {
    fontSize: "14px",
    color: "#fff",
  },
  fileInput: {
    padding: "10px",
    borderRadius: "8px",
    background: "rgba(255,255,255,0.15)",
    border: "none",
    color: "#fff",
  },
  submitButton: {
    background:
      "linear-gradient(90deg, rgba(99,102,241,1) 0%, rgba(168,85,247,1) 100%)",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    padding: "12px",
    cursor: "pointer",
    fontWeight: "600",
  },
  message: {
    marginTop: "15px",
    color: "#ffbdbd",
  },
  subHeading: {
    marginTop: "40px",
    fontSize: "18px",
    fontWeight: "500",
  },
  tableContainer: {
    marginTop: "10px",
    background: "rgba(255,255,255,0.05)",
    borderRadius: "10px",
    overflowX: "auto",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
  },
  th: {
    padding: "10px",
    textAlign: "left",
    borderBottom: "1px solid rgba(255,255,255,0.2)",
  },
  td: {
    padding: "10px",
    borderBottom: "1px solid rgba(255,255,255,0.1)",
  },
  link: {
    color: "#a78bfa",
    textDecoration: "underline",
  },
};
