import { useState } from "react";

export default function AddEmployee() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [position, setPosition] = useState("");
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      // Step 1: Upload the file to Supabase Storage
      const formData = new FormData();
      formData.append("file", file);

      const uploadRes = await fetch("https://development-p6rb.onrender.com/upload", {
        method: "POST",
        body: formData,
      });

      const uploadData = await uploadRes.json();

      if (uploadData.error) {
        setMessage("File upload failed!");
        return;
      }

      // Step 2: Save employee data with uploaded file URL
      const res = await fetch("https://development-p6rb.onrender.com/add-employee", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          email,
          position,
          file_url: uploadData.file_url, // 👈 include uploaded file URL
        }),
      });

      const data = await res.json();
      setMessage(data.message || data.error);

      // Reset form
      setName("");
      setEmail("");
      setPosition("");
      setFile(null);
    } catch (err) {
      setMessage("Something went wrong!");
    }
  };

  return (
    <div>
      <h2>Add Employee</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Position"
          value={position}
          onChange={(e) => setPosition(e.target.value)}
          required
        />
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
          required
        />
        <button type="submit">Add Employee</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}