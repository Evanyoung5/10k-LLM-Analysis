import fitz  # PyMuPDF
from typing import List

def parse_pdf(pdf_bytes: bytes, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    # Split into chunks with overlap
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks
