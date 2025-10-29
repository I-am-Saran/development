import React, { useState } from 'react';

const BulkUpload = () => {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') {
      setFile(selectedFile);
    } else {
      alert("Please upload a valid Excel file.");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('https://development-p6rb.onrender.com/bulk_upload', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setMessage(data.message || "Upload Successful!");
    } catch (error) {
      setMessage("Something went wrong!");
      console.error(error);
    }
  };

  return (
    <div>
      <h2>Upload Excel File</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept=".xlsx"
          onChange={handleFileChange}
          required
        />
        <button type="submit">Submit</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default BulkUpload;
