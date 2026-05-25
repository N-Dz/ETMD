import json
import os
import re

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

_model = genai.GenerativeModel("gemini-1.5-flash")

DC_ELEMENTS = [
    "title", "creator", "subject", "description", "publisher",
    "contributor", "date", "type", "format", "identifier",
    "source", "language", "relation", "coverage", "rights",
]


def classify(input_str: str) -> str:
    """Return one of: 'pdf', 'url', 'doi'."""
    prompt = (
        "Classify the following input as exactly one of these types: pdf, url, doi.\n"
        "Rules:\n"
        "- 'pdf' if it is a filename ending in .pdf\n"
        "- 'doi' if it looks like a DOI (starts with '10.' or 'doi:' or 'https://doi.org/')\n"
        "- 'url' if it is a web URL\n"
        "Respond with a single word: pdf, url, or doi.\n\n"
        f"Input: {input_str}"
    )
    response = _model.generate_content(prompt)
    result = response.text.strip().lower()
    for t in ("pdf", "url", "doi"):
        if t in result:
            return t
    return "url"


def enrich(raw_dict: dict) -> dict:
    keys = ", ".join(DC_ELEMENTS)
    prompt = (
        "Given the following raw metadata, produce a Dublin Core record.\n"
        "Fill in missing fields where you can reasonably infer them.\n"
        f"Return ONLY valid JSON with exactly these keys (omit keys you cannot fill): {keys}\n\n"
        f"Raw metadata:\n{json.dumps(raw_dict, indent=2)}"
    )
    response = _model.generate_content(prompt)
    text = response.text.strip()

    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    return json.loads(text)
