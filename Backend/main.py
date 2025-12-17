from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import os
import mimetypes
from docx2pdf import convert


# PDF → Word
from pdf2docx import Converter

# Word → PDF
from docx import Document
from reportlab.pdfgen import canvas

# FastAPI Ap
app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Upload API
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": file.filename}

# PDF → Word API
@app.post("/convert/pdf-to-word")
def pdf_to_word(filename: str):
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    pdf_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    word_filename = filename.replace(".pdf", ".docx")
    word_path = os.path.join(OUTPUT_DIR, word_filename)
    
    converter = Converter(pdf_path)
    converter.convert(word_path)
    converter.close()
    
    return {"output_file": word_filename}

# Word → PDF API
@app.post("/convert/word-to-pdf")
def word_to_pdf(filename: str):
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    doc_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(doc_path):
        raise HTTPException(status_code=404, detail="Word file not found")

    if not filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only DOCX files allowed")

    pdf_filename = filename.replace(".docx", ".pdf")
    pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)

    try:
        convert(doc_path, pdf_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"output_file": pdf_filename}


# Download API

@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path,
        media_type="application/octet-stream",  # Forces download
        filename=filename
    )

# # Preview API (for PDF preview in browser)

# @app.get("/preview/{filename}")
# def preview_file(filename: str):
#     file_path = os.path.join(OUTPUT_DIR, filename)
    
#     if not os.path.exists(file_path):
#         raise HTTPException(status_code=404, detail="File not found")
    
#     # Detect MIME type for browser preview
#     mime_type, _ = mimetypes.guess_type(file_path)
    
#     return FileResponse(
#         file_path,
#         media_type=mime_type or "application/pdf"
#     )
