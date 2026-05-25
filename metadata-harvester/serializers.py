from models import DublinCore


def to_json_dc(model: DublinCore) -> dict:
    return model.model_dump(exclude_none=True)


def to_jsonld(model: DublinCore) -> dict:
    data = model.model_dump(exclude_none=True)
    return {
        "@context": "http://purl.org/dc/elements/1.1/",
        "@type": "Resource",
        **data,
    }
