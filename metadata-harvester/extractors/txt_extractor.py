def extract(file_bytes: bytes, filename: str = "") -> dict:
    text = file_bytes.decode("utf-8", errors="replace")
    return {"filename": filename, "content": text[:4000]}
