import fitz  # PyMuPDF
import re
from typing import List, Dict


def parse_pdf_sections(pdf_bytes: bytes, chunk_size: int = 500, overlap: int = 100) -> List[Dict]:
    """
    Parse a PDF and split it into section-aware chunks suitable for embedding.
    Returns a list of dictionaries with 'section' and 'text' keys.
    """
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap.")
    
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        raise ValueError("Could not open PDF file. Check if it's a valid PDF.") from e

    # Extract full text
    full_text = ""
    for i, page in enumerate(doc):
        page_text = page.get_text()
        if not page_text.strip():
            print(f"Warning: Page {i + 1} has no extractable text.")
        full_text += page_text + "\n"

    # Define regex to find 10-K style section headers
    section_pattern = re.compile(r'\n?(Item\s+(\d+[A-Z]?)\.?)', re.IGNORECASE)
    matches = list(section_pattern.finditer(full_text))

    sections = []
    for idx, match in enumerate(matches):
        section_title = match.group(1).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(full_text)
        section_text = full_text[start:end].strip()

        if not section_text:
            continue

        # Chunk the section text if it's too long
        words = section_text.split()
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words).strip()
            if chunk_text:
                sections.append({
                    "section": section_title,
                    "text": chunk_text
                })

    return sections
