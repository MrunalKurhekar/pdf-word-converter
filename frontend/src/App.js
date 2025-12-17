import React, { useState } from "react";
import API from "./Api";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [uploadedFileName, setUploadedFileName] = useState("");
  const [convertedFile, setConvertedFile] = useState("");

  // Upload File

  const uploadFile = async () => {
    if (!file) {
      alert("Please select a file first");
      return;
    }

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await API.post("/upload", formData);

      console.log("Uploaded file:", response.data.filename);

      setUploadedFileName(response.data.filename);

      alert("File uploaded successfully");
    } catch (error) {
      console.error(error);
      alert("Upload failed");
    }
  };

  // PDF → Word

  const pdfToWord = async () => {
    console.log("Trying to convert:", uploadedFileName);

    if (!uploadedFileName || !uploadedFileName.endsWith(".pdf")) {
      alert("Please upload a PDF first");
      return;
    }

    try {
      const response = await API.post("/convert/pdf-to-word", null, {
        params: { filename: uploadedFileName },
      });

      setConvertedFile(response.data.output_file);
    } catch (error) {
      alert(error.response?.data?.detail || "Conversion failed");
    }
  };

  // Word → PDF

  const wordToPdf = async () => {
    if (!uploadedFileName) {
      alert("Please upload a Word file first");
      return;
    }

    await API.post("/convert/word-to-pdf", null, {
      params: { filename: uploadedFileName },
    })
      .then((res) => setConvertedFile(res.data.output_file))
      .catch((err) => alert(err.response.data.detail));
  };
  return (
    <div className="container">
      <h1>Convert PDF ↔ Word </h1>

      <input type="file" onChange={(e) => setFile(e.target.files[0])} />

      <button onClick={uploadFile}>Upload File</button>

      <div className="buttons">
        <button onClick={pdfToWord}>PDF → Word</button>
        <button onClick={wordToPdf}>Word → PDF</button>
      </div>

      {convertedFile && (
        <div className="result">
          <h3>Download</h3>

          {/* PDF Preview */}
          {/* {convertedFile.endsWith(".pdf") && (
            <iframe
              src={`http://localhost:8000/download/${convertedFile}`}
              width="100%"
              height="400px"
              title="PDF Preview"
            ></iframe>
          )} */}

          <a href={`http://localhost:8000/download/${convertedFile}`} download>
            {" "}
            Download File
          </a>
        </div>
      )}
    </div>
  );
}

export default App;
