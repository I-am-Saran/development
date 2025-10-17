import { useState, useEffect } from "react";
import { useState, useRef } from "react";


export default function AddEmployee() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [position, setPosition] = useState("");
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [employees, setEmployees] = useState([]);
  const fileInputRef = useRef();

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

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append("name", name);
    formData.append("email", email);
    formData.append("position", position);
    formData.append("file", file);

    try {
      const res = await fetch("https://development-p6rb.onrender.com/add-employee", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setMessage(data.message || data.error);
    } catch (err) {
      console.error(err);
      setMessage("Something went wrong!");
    }

    // Reset form
    setName("");
    setEmail("");
    setPosition("");
    setFile(null);

    if (fileInputRef.current) {
    fileInputRef.current.value = "";
    }
    // Refresh employee table
    fetchEmployees();
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>Add Employee</h2>

      {/* Form */}
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
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
          style={styles.fileInput}
          ref={fileInputRef}
        />
        <button type="submit" style={styles.button}>Add Employee</button>
      </form>

      {message && <p style={styles.message}>{message}</p>}

      {/* Employee Table */}
      <h3 style={styles.tableHeading}>Employee List</h3>
      <div style={styles.tableContainer}>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Name</th>
              <th style={styles.th}>Email</th>
              <th style={styles.th}>Position</th>
              <th style={styles.th}>File</th>
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