import requests


def extract(doi: str) -> dict:
    doi = doi.strip().lstrip("https://doi.org/").lstrip("http://doi.org/")
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url, timeout=15, headers={"User-Agent": "metadata-harvester/1.0"})
    response.raise_for_status()

    msg = response.json().get("message", {})
    raw = {"doi": doi}

    if msg.get("title"):
        raw["title"] = msg["title"][0]
    if msg.get("author"):
        authors = [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in msg["author"]]
        raw["author"] = "; ".join(authors)
    if msg.get("publisher"):
        raw["publisher"] = msg["publisher"]
    if msg.get("container-title"):
        raw["container_title"] = msg["container-title"][0]
    if msg.get("issued", {}).get("date-parts"):
        parts = msg["issued"]["date-parts"][0]
        raw["issued"] = "-".join(str(p) for p in parts if p)
    if msg.get("abstract"):
        raw["abstract"] = msg["abstract"]
    if msg.get("language"):
        raw["language"] = msg["language"]
    if msg.get("URL"):
        raw["url"] = msg["URL"]
    if msg.get("ISSN"):
        raw["issn"] = "; ".join(msg["ISSN"])
    if msg.get("subject"):
        raw["subject"] = "; ".join(msg["subject"])
    if msg.get("license"):
        raw["license"] = msg["license"][0].get("URL", "")

    return {k: v for k, v in raw.items() if v}
