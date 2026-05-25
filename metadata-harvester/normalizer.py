from models import DublinCore


def normalize(enriched_dict: dict) -> DublinCore:
    # Pydantic ignores unknown keys; cast all values to str or None
    clean = {k: str(v) if v is not None else None for k, v in enriched_dict.items()}
    return DublinCore(**clean)
