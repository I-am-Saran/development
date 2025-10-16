import { useState } from "react";

export default function AddEmployee() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [position, setPosition] = useState("");
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

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

  // reset form
  setName("");
  setEmail("");
  setPosition("");
  setFile(null);
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