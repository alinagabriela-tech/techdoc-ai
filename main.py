
from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from pypdf import PdfReader

app = FastAPI(
    title="TechDoc AI",
    description="An assistant for searching and answering questions about technical documents.",
    version="0.2.0",
)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {".pdf", ".txt"}


@app.get("/")
def home():
    return {
        "message": "Welcome to TechDoc AI!",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/documents/read")
async def read_document(file: UploadFile = File(...)):
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Upload a PDF or TXT file.",
        )

    content = await file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File too large. Maximum size is 5 MB.",
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    try:
        if extension == ".txt":
            text = content.decode("utf-8-sig")
        else:
            reader = PdfReader(BytesIO(content))

            if reader.is_encrypted:
                raise HTTPException(
                    status_code=400,
                    detail="Password-protected PDFs are not supported.",
                )

            text = "\n".join(
                page.extract_text() or "" for page in reader.pages
            )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not read this file. Check that it is a valid PDF or UTF-8 text file.",
        )

    text = text.strip()

    if not text:
        raise HTTPException(
            status_code=422,
            detail="No extractable text was found in this document.",
        )

    return {
        "filename": Path(file.filename or "document").name,
        "characters": len(text),
        "text_preview": text[:3000],
        "truncated": len(text) > 3000,
    }
