import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./components/Login";
import AddEmployee from "./components/AddEmployee";
import BulkUpload from "./BulkUpload/BulkUpload";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/add-employee" element={<AddEmployee />} />
        <Route path="/bulk-upload" element={<BulkUpload />} />
      </Routes>
    </Router>
  );
}

export default App;