import requests
from bs4 import BeautifulSoup


def extract(url: str) -> dict:
    response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    raw = {"source_url": url}

    # Open Graph tags
    for tag in soup.find_all("meta", property=True):
        prop = tag.get("property", "")
        if prop.startswith("og:"):
            raw[prop[3:]] = tag.get("content", "")

    # Standard meta name tags
    for tag in soup.find_all("meta", attrs={"name": True}):
        name = tag.get("name", "").lower()
        content = tag.get("content", "")
        if name and content:
            raw[name] = content

    # Fallback: page title
    if "title" not in raw and soup.title:
        raw["title"] = soup.title.string

    return {k: v for k, v in raw.items() if v}
