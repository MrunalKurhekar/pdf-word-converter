import React, { useState, useRef } from "react";
import API from "./Api";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [uploadedFileName, setUploadedFileName] = useState("");
  const [convertedFile, setConvertedFile] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const resultRef = useRef(null);

  // File Selection
  const handleFileChange = (e) => {
    const selected = e.target.files[0];

    setConvertedFile("");
    setUploadedFileName("");
    setMessage("");

    if (!selected) return;

    if (selected.size > 10 * 1024 * 1024) {
      setMessage("File must be less than 10MB");
      return;
    }

    setFile(selected);
  };

  // Upload File
  const uploadFile = async () => {
    if (!file) {
      setMessage("Please select a file first");
      return;
    }

    try {
      setLoading(true);
      setMessage("");

      const formData = new FormData();
      formData.append("file", file);

      const response = await API.post("/upload", formData);

      setUploadedFileName(response.data.filename);
      setMessage("File uploaded successfully ✅");
    } catch (error) {
      console.error(error);
      setMessage(
        error.response?.data?.detail ||
          "Upload failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  // Convert PDF → Word
  const pdfToWord = async () => {
    if (!uploadedFileName.endsWith(".pdf")) {
      setMessage("Please upload a PDF file first");
      return;
    }

    try {
      setLoading(true);
      setMessage("");

      const response = await API.post("/convert/pdf-to-word", null, {
        params: { filename: uploadedFileName },
      });

      setConvertedFile(response.data.output_file);

      setTimeout(() => {
        resultRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 300);
    } catch (error) {
      console.error(error);
      setMessage(
        error.response?.data?.detail ||
          "PDF to Word conversion failed."
      );
    } finally {
      setLoading(false);
    }
  };

  // Convert Word → PDF
  const wordToPdf = async () => {
    if (!uploadedFileName.endsWith(".docx")) {
      setMessage("Please upload a Word (.docx) file first");
      return;
    }

    try {
      setLoading(true);
      setMessage("");

      const response = await API.post("/convert/word-to-pdf", null, {
        params: { filename: uploadedFileName },
      });

      setConvertedFile(response.data.output_file);

      setTimeout(() => {
        resultRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 300);
    } catch (error) {
      console.error(error);
      setMessage(
        error.response?.data?.detail ||
          "Word to PDF conversion failed."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <header>
        <h1>PDF Converter Pro</h1>
        <p>Fast • Secure • Free Online PDF Tool</p>
      </header>

      <div className="card">
        <input
          type="file"
          accept=".pdf,.docx"
          onChange={handleFileChange}
        />

        {file && (
          <p className="file-name">
            Selected File: <strong>{file.name}</strong>
          </p>
        )}

        <button
          className="upload-btn"
          onClick={uploadFile}
          disabled={loading}
        >
          {loading ? "Uploading..." : "Upload File"}
        </button>

        <div className="buttons">
          <button onClick={pdfToWord} disabled={loading}>
            PDF → Word
          </button>
          <button onClick={wordToPdf} disabled={loading}>
            Word → PDF
          </button>
        </div>

        {loading && (
          <p className="loading">
            Processing... Please wait ⏳
          </p>
        )}

        {message && <p className="message">{message}</p>}

        {convertedFile && (
          <div className="result" ref={resultRef}>
            <h3>Download Converted File</h3>
            <a
              href={`${process.env.REACT_APP_API_URL}/download/${convertedFile}`}
              download
              className="download-btn"
              target="_blank"
              rel="noopener noreferrer"
            >
              Download File
            </a>
          </div>
        )}
      </div>

      <section className="info-section">
        <h2>Why Choose Our PDF Converter?</h2>
        <p>
          Convert PDF to Word and Word to PDF instantly.
          Files are processed securely and deleted
          automatically after conversion.
        </p>
      </section>

      <section className="info-section">
        <h2>How It Works</h2>
        <p>1. Upload your file</p>
        <p>2. Select conversion type</p>
        <p>3. Download instantly</p>
      </section>

      <footer>
        <p>© 2026 PDF Converter Pro</p>
        <p>Privacy Policy | Terms & Conditions | Contact</p>
      </footer>
    </div>
  );
}

export default App;