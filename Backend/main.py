from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import subprocess
import uuid
import shutil
from PyPDF2 import PdfReader
from pdf2docx import Converter
from fastapi import BackgroundTasks
import platform
import shutil

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
origins = [
    "https://pdf-word-converter-frontend.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # allow your frontend
    allow_credentials=True,
    allow_methods=["*"],          # allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],          # allow all headers
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

    # 🔥 Proper cross-platform detection
    if platform.system() == "Windows":
        office_cmd = r"C:\Program Files\LibreOffice\program\soffice.exe"
    else:
        office_cmd = shutil.which("libreoffice") or shutil.which("soffice")

    if not office_cmd:
        raise HTTPException(
            status_code=500,
            detail="LibreOffice is not installed on server"
        )

    try:
        subprocess.run(
            [
                office_cmd,
                "--headless",
                "--convert-to",
                "pdf",
                doc_path,
                "--outdir",
                OUTPUT_DIR,
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Word to PDF conversion failed: {str(e)}"
        )

    return {
        "message": "Conversion successful",
        "output_file": pdf_filename
    }

# -----------------------------
# Download API
# -----------------------------
@app.get("/download/{filename}")
def download_file(filename: str, background_tasks: BackgroundTasks):

    file_path = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    # Delete file after response
    background_tasks.add_task(os.remove, file_path)

    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=filename
    )
