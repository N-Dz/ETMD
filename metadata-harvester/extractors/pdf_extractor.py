import fitz  # PyMuPDF


def extract(file_bytes: bytes) -> dict:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    meta = doc.metadata or {}
    doc.close()
    return {k: v for k, v in meta.items() if v}
