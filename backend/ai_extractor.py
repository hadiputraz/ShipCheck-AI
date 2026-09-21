import json
import os
import re
from typing import Any

from openai import OpenAI


MODEL = os.getenv("SHIPCHECK_AI_MODEL", "gpt-5.6-luna")


REQUIRED_FIELDS = [
    "shipper",
    "consignee",
    "notify_party",
    "port_of_loading",
    "port_of_discharge",
    "container_count",
    "gross_weight_kg",
]


def is_available():
    return bool(os.getenv("OPENAI_API_KEY"))


def _clean_text(value):
    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


def _normalize_for_support(value):
    if value is None:
        return ""

    value = str(value).upper()
    value = value.replace("×", "X")
    value = re.sub(r"\s+", "", value)

    return value


def candidate_is_supported(candidate, source_text):
    """
    Safety check:
    Only accept an AI-extracted value when a normalized form
    can actually be found in the source document text.
    """
    if candidate is None:
        return False

    candidate_norm = _normalize_for_support(candidate)
    source_norm = _normalize_for_support(source_text)

    if not candidate_norm or not source_norm:
        return False

    return candidate_norm in source_norm


def _build_prompt(document_type, document_text):
    return f"""
You are the document extraction component of ShipCheck AI.

Extract fields from this {document_type}.

IMPORTANT RULES:
1. Extract only information explicitly present in the document.
2. Never guess.
3. Never infer a value from context.
4. If a field is not clearly present, return null.
5. Preserve the actual value as written, without inventing formatting.
6. For gross_weight_kg, return the numeric weight when clearly visible.
7. For container_count, preserve values such as "3 x 40'HC".
8. Return ONLY valid JSON.
9. Include evidence for every non-null field using a short exact excerpt from the source.
10. If the evidence is not explicitly present, the field must be null.

Required JSON structure:

{{
  "fields": {{
    "shipper": null,
    "consignee": null,
    "notify_party": null,
    "port_of_loading": null,
    "port_of_discharge": null,
    "container_count": null,
    "gross_weight_kg": null
  }},
  "confidence": {{
    "shipper": 0.0,
    "consignee": 0.0,
    "notify_party": 0.0,
    "port_of_loading": 0.0,
    "port_of_discharge": 0.0,
    "container_count": 0.0,
    "gross_weight_kg": 0.0
  }},
  "evidence": {{
    "shipper": null,
    "consignee": null,
    "notify_party": null,
    "port_of_loading": null,
    "port_of_discharge": null,
    "container_count": null,
    "gross_weight_kg": null
  }}
}}

DOCUMENT:

{document_text}
"""


def extract_with_ai(document_type, document_text):
    if not is_available():
        return {
            "enabled": False,
            "model": MODEL,
            "fields": {},
            "confidence": {},
            "evidence": {},
            "reason": "OPENAI_API_KEY is not configured.",
        }

    if not document_text or not str(document_text).strip():
        return {
            "enabled": True,
            "model": MODEL,
            "fields": {},
            "confidence": {},
            "evidence": {},
            "reason": "Document text is empty.",
        }

    client = OpenAI()

    response = client.responses.create(
        model=MODEL,
        input=_build_prompt(
            document_type,
            str(document_text),
        ),
    )

    raw_output = response.output_text.strip()

    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"AI returned invalid JSON: {exc}"
        ) from exc

    fields = data.get("fields", {})
    confidence = data.get("confidence", {})
    evidence = data.get("evidence", {})

    cleaned_fields = {}
    cleaned_confidence = {}
    cleaned_evidence = {}

    for field in REQUIRED_FIELDS:
        candidate = _clean_text(fields.get(field))
        score = confidence.get(field, 0.0)
        excerpt = _clean_text(evidence.get(field))

        try:
            score = float(score)
        except (TypeError, ValueError):
            score = 0.0

        if candidate and candidate_is_supported(
            candidate,
            document_text,
        ):
            cleaned_fields[field] = candidate
            cleaned_confidence[field] = max(
                0.0,
                min(1.0, score),
            )
            cleaned_evidence[field] = excerpt
        else:
            cleaned_fields[field] = None
            cleaned_confidence[field] = 0.0
            cleaned_evidence[field] = None

    return {
        "enabled": True,
        "model": MODEL,
        "fields": cleaned_fields,
        "confidence": cleaned_confidence,
        "evidence": cleaned_evidence,
        "reason": None,
    }
