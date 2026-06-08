import json
import os
import re

from groq import Groq
from dotenv import load_dotenv

load_dotenv()
_client = Groq(api_key=os.environ["GROQ_API_KEY"])
_MODEL = "llama-3.1-8b-instant"


def _generate(prompt: str) -> str:
    response = _client.chat.completions.create(
        model=_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

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
    result = _generate(prompt).strip().lower()
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
    text = _generate(prompt)

    # Extract the first JSON object from the response
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in LLM response: {text!r}")

    return json.loads(match.group())
