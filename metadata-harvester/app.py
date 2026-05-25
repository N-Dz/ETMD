import json
import sys
import os

import streamlit as st

# Ensure local modules resolve correctly when run via `streamlit run`
sys.path.insert(0, os.path.dirname(__file__))

from orchestrator import classify, enrich
from extractors import pdf_extractor, url_extractor, doi_extractor
from normalizer import normalize
from serializers import to_json_dc, to_jsonld

st.set_page_config(page_title="Metadata Harvester", layout="centered")
st.title("Metadata Harvester")
st.caption("Extract and normalize metadata to Dublin Core from a URL, DOI, or PDF.")

# --- Input section ---
input_type = st.radio("Input type", ["URL", "DOI", "PDF"], horizontal=True)

user_input = None
uploaded_file = None

if input_type == "PDF":
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
else:
    label = "Enter a URL" if input_type == "URL" else "Enter a DOI (e.g. 10.1038/nature12373)"
    user_input = st.text_input(label)

extract_btn = st.button("Extract Metadata", type="primary")

# --- Extraction logic ---
if extract_btn:
    raw_dict = None
    input_label = None

    try:
        if input_type == "PDF":
            if not uploaded_file:
                st.error("Please upload a PDF file.")
                st.stop()
            with st.spinner("Reading PDF metadata..."):
                raw_dict = pdf_extractor.extract(uploaded_file.read())
            input_label = uploaded_file.name

        elif input_type == "URL":
            if not user_input:
                st.error("Please enter a URL.")
                st.stop()
            with st.spinner("Fetching page metadata..."):
                raw_dict = url_extractor.extract(user_input)
            input_label = user_input

        else:  # DOI
            if not user_input:
                st.error("Please enter a DOI.")
                st.stop()
            with st.spinner("Querying CrossRef..."):
                raw_dict = doi_extractor.extract(user_input)
            input_label = user_input

        with st.spinner("Enriching with Gemini..."):
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
