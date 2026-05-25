# Plan: Metadata Harvesting Tool (ETMD)

## Context
Student project requiring a tool that accepts a URL, DOI, or PDF file, extracts raw metadata via dedicated extractors, normalizes it to Dublin Core standard, and outputs JSON and JSON-LD formats. The LLM (Gemini) acts as both a router (classifying input type) and an enricher (filling missing/ambiguous Dublin Core fields after extraction). Frontend is Streamlit for simplicity. No persistence — results are displayed in-session and downloadable.

## Decisions Made
| Concern | Decision |
|---|---|
| Frontend | Streamlit |
| LLM | Google Gemini 1.5 Flash (free tier) |
| LLM role | Router + enricher (2 calls) |
| Input types | PDF, URL, DOI |
| Output formats | Dublin Core JSON + JSON-LD |
| Storage | In-session only (download buttons) |
| Batch | Single input per request |

---

## Project Structure

```
metadata-harvester/
├── app.py                  # Streamlit UI
├── orchestrator.py         # Gemini: classify input + enrich metadata
├── extractors/
│   ├── __init__.py
│   ├── pdf_extractor.py    # PyMuPDF -> raw metadata dict
│   ├── url_extractor.py    # requests + BeautifulSoup (Open Graph/meta tags)
│   └── doi_extractor.py    # CrossRef REST API
├── normalizer.py           # Validate + structure into DublinCore Pydantic model
├── serializers.py          # Render DC model -> JSON and JSON-LD dicts
├── models.py               # DublinCore Pydantic model (15 DC elements)
├── .env                    # GEMINI_API_KEY
└── requirements.txt
```

---

## Implementation Steps

### Step 1: Bootstrap
- Create `metadata-harvester/` directory and all files above
- `requirements.txt`:
  ```
  streamlit
  google-generativeai
  pymupdf
  requests
  beautifulsoup4
  pydantic
  python-dotenv
  ```

### Step 2: `models.py` — Dublin Core schema
- Pydantic model with all 15 DC elements as `Optional[str]`
- Elements: title, creator, subject, description, publisher, contributor, date, type, format, identifier, source, language, relation, coverage, rights

### Step 3: Extractors
- **`pdf_extractor.py`**: Use `fitz` (PyMuPDF) to read `doc.metadata` dict. Return raw dict.
- **`url_extractor.py`**: `requests.get(url)` + BeautifulSoup. Parse `<meta>` Open Graph tags (`og:title`, `og:description`, etc.) and standard `<meta name>` tags. Return raw dict.
- **`doi_extractor.py`**: `GET https://api.crossref.org/works/{doi}` — no auth needed. Parse response `message` object. Return raw dict.

### Step 4: `orchestrator.py` — Gemini integration
- **Call 1 — Router**: Send the raw input string (or filename for PDF) to Gemini with a prompt asking it to classify as one of: `pdf`, `url`, `doi`. Parse response to get type string.
- **Call 2 — Enricher**: After extractor returns raw dict, send it to Gemini with a prompt: *"Given this raw metadata, produce a Dublin Core record. Fill in missing fields where you can infer them. Return valid JSON with only these keys: [15 DC elements]."* Parse JSON response.
- Use `google-generativeai` SDK: `genai.GenerativeModel('gemini-1.5-flash').generate_content(prompt)`

### Step 5: `normalizer.py`
- Accept the enriched dict from Gemini
- Instantiate `DublinCore(**enriched_dict)` — Pydantic validates and drops unknown keys
- Return the model instance

### Step 6: `serializers.py`
- `to_json_dc(model)` — `model.model_dump(exclude_none=True)`
- `to_jsonld(model)` — wrap in JSON-LD context:
  ```json
  {
    "@context": "http://purl.org/dc/elements/1.1/",
    "@type": "Resource",
    ...dc fields...
  }
  ```

### Step 7: `app.py` — Streamlit UI
Layout:
```
Title: "Metadata Harvester"
---
Input section:
  - Radio: [URL | DOI | PDF upload]
  - Text input (URL/DOI) OR file_uploader (PDF)
  - [Extract Metadata] button
---
Results section (after extraction):
  - st.json() display of Dublin Core JSON
  - st.download_button() -> JSON file
  - st.download_button() -> JSON-LD file
  - st.expander("Raw extractor output") for debugging
```

---

## Key Libraries & Their Roles
| Library | Role |
|---|---|
| `google-generativeai` | Gemini API (routing + enrichment) |
| `pymupdf` (`fitz`) | PDF metadata extraction |
| `requests` + `beautifulsoup4` | URL scraping |
| CrossRef REST API | DOI lookup (no key needed) |
| `pydantic` | Dublin Core model validation |
| `streamlit` | UI |
| `python-dotenv` | Load `GEMINI_API_KEY` from `.env` |

---

## Data Flow (concrete)
```
User input
  |
app.py -> orchestrator.classify(input)
  |          -> Gemini Call 1: returns "doi" | "url" | "pdf"
  |
  -> extractor.extract(input)        # doi_extractor / url_extractor / pdf_extractor
  |          -> returns raw_dict
  |
  -> orchestrator.enrich(raw_dict)
  |          -> Gemini Call 2: returns enriched DC dict (JSON)
  |
  -> normalizer.normalize(enriched_dict)
  |          -> returns DublinCore model
  |
  -> serializers.to_json_dc(model)   # JSON output
  -> serializers.to_jsonld(model)    # JSON-LD output
  |
app.py displays results + download buttons
```

---

## Verification
1. Run `streamlit run app.py`
2. Test DOI input: `10.1038/nature12373` — should return CrossRef data normalized to DC
3. Test URL input: a Wikipedia article URL — should return Open Graph metadata
4. Test PDF upload: any PDF with metadata — should return author/title/date
5. Verify JSON output has only valid Dublin Core keys
6. Verify JSON-LD output has `@context` and `@type` fields
7. Verify download buttons produce valid files
