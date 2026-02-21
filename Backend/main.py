from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import subprocess
import uuid
import shutil
from PyPDF2 import PdfReader
from pdf2docx import Converter

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI()

@app.get("/")
def home():
    return {
        "status": "OK",
        "message": "PDF Converter API is running"
    }

# -----------------------------
# Enable CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Directories
# -----------------------------
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAX_SIZE = 10 * 1024 * 1024  # 10MB


# -----------------------------
# Upload API
# -----------------------------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    contents = await file.read()

    if len(contents) > MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large. Max 10MB allowed."
        )

    # Generate secure unique filename
    unique_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to save file"
        )

    return {"filename": unique_name}


# -----------------------------
# PDF → Word API
# -----------------------------
@app.post("/convert/pdf-to-word")
def pdf_to_word(filename: str):

    if not filename or not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files allowed"
        )

    pdf_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(pdf_path):
        raise HTTPException(
            status_code=404,
            detail="PDF file not found"
        )

    # Validate PDF content
    try:
        reader = PdfReader(pdf_path)

        if len(reader.pages) == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty PDF file"
            )

        if not reader.pages[0].extract_text():
            raise HTTPException(
                status_code=400,
                detail="Scanned PDFs are not supported"
            )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Unable to read PDF content"
        )

    word_filename = filename.replace(".pdf", ".docx")
    word_path = os.path.join(OUTPUT_DIR, word_filename)

    try:
        converter = Converter(pdf_path)
        converter.convert(word_path)
        converter.close()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Conversion failed: {str(e)}"
        )

    return {"output_file": word_filename}


# -----------------------------
# Word → PDF API (LibreOffice)
# -----------------------------
@app.post("/convert/word-to-pdf")
def word_to_pdf(filename: str):

    if not filename or not filename.lower().endswith(".docx"):
        raise HTTPException(
            status_code=400,
            detail="Only DOCX files allowed"
        )

    doc_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(doc_path):
        raise HTTPException(
            status_code=404,
            detail="Word file not found"
        )

    base_name = os.path.splitext(filename)[0]
    pdf_filename = f"{base_name}.pdf"

    try:
        subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                "pdf",
                doc_path,
                "--outdir",
                OUTPUT_DIR,
            ],
            check=True,
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="LibreOffice is not installed on server"
        )
    except subprocess.CalledProcessError:
        raise HTTPException(
            status_code=500,
            detail="Word to PDF conversion failed"
        )

    return {
        "message": "Conversion successful",
        "output_file": pdf_filename
    }


# -----------------------------
# Download API
# -----------------------------
@app.get("/download/{filename}")
def download_file(filename: str):

    file_path = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    response = FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=filename
    )

    # Auto delete after download
    @response.call_on_close
    def cleanup():
        try:
            os.remove(file_path)
        except Exception:
            pass

    return response