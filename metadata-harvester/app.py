import json
import sys
import os

import streamlit as st

# Ensure local modules resolve correctly when run via `streamlit run`
sys.path.insert(0, os.path.dirname(__file__))

from orchestrator import classify, enrich
from extractors import pdf_extractor, url_extractor, doi_extractor, txt_extractor, csv_extractor
from normalizer import normalize
from serializers import to_json_dc, to_jsonld

FILE_EXTRACTORS = {
    "pdf": lambda b, n: pdf_extractor.extract(b),
    "txt": txt_extractor.extract,
    "csv": csv_extractor.extract,
}

TEXT_EXTRACTORS = {
    "url": lambda s: url_extractor.extract(s),
    "doi": lambda s: doi_extractor.extract(s),
}

st.set_page_config(page_title="Metadata Harvester", layout="centered")
st.title("Metadata Harvester")
st.caption("Extract and normalize metadata to Dublin Core. Drop a file or paste a URL/DOI — the type is detected automatically.")

# --- Input section ---
uploaded_file = st.file_uploader("Upload a file (PDF, TXT, CSV)", type=["pdf", "txt", "csv"])
user_input = st.text_input("Or paste a URL or DOI")

extract_btn = st.button("Extract Metadata", type="primary")

# --- Extraction logic ---
if extract_btn:
    raw_dict = None
    input_label = None

    try:
        if uploaded_file:
            ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
            file_bytes = uploaded_file.read()
            with st.spinner(f"Reading {ext.upper()} file..."):
                raw_dict = FILE_EXTRACTORS[ext](file_bytes, uploaded_file.name)
            input_label = uploaded_file.name

        elif user_input:
            with st.spinner("Classifying input..."):
                input_type = classify(user_input)
            st.info(f"Detected input type: **{input_type.upper()}**")
            with st.spinner("Extracting metadata..."):
                raw_dict = TEXT_EXTRACTORS[input_type](user_input)
            input_label = user_input

        else:
            st.error("Please upload a PDF or enter a URL/DOI.")
            st.stop()

        with st.spinner("Enriching with LLM..."):
            enriched = enrich(raw_dict)

        dc_model = normalize(enriched)
        json_dc = to_json_dc(dc_model)
        jsonld = to_jsonld(dc_model)

    except Exception as e:
        st.error(f"Extraction failed: {e}")
        st.stop()

    # --- Results section ---
    st.success("Metadata extracted successfully.")

    st.subheader("Dublin Core (JSON)")
    st.json(json_dc)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Download JSON",
            data=json.dumps(json_dc, indent=2, ensure_ascii=False),
            file_name="metadata_dc.json",
            mime="application/json",
        )
    with col2:
        st.download_button(
            label="Download JSON-LD",
            data=json.dumps(jsonld, indent=2, ensure_ascii=False),
            file_name="metadata_dc.jsonld",
            mime="application/ld+json",
        )

    with st.expander("Raw extractor output (debug)"):
        st.json(raw_dict)
