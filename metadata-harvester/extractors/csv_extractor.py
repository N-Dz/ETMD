import csv
import io


def extract(file_bytes: bytes, filename: str = "") -> dict:
    text = file_bytes.decode("utf-8", errors="replace")
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        return {"filename": filename}
    columns = rows[0]
    sample = rows[1:6]  # up to 5 data rows
    return {"filename": filename, "columns": columns, "sample": sample, "row_count": len(rows) - 1}
