import json
from pathlib import Path

from classifier import classify_email
from extractor import extract_document
from parser import parse_document
from normalizer import normalize_fields
from comparator import compare_documents


BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "sdoc-hackathon-bundle"


def load_email(email_id):
    path = DATA_DIR / "inbox" / f"{email_id}.json"

    if not path.exists():
        raise FileNotFoundError(
            f"Email not found: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def resolve_attachment(relative_path):
    return DATA_DIR / relative_path


def find_si_and_bl(attachments):

    si_path = None
    bl_path = None

    for attachment in attachments:

        name = Path(attachment).name.upper()

        if "_SI." in name:
            si_path = resolve_attachment(
                attachment
            )

        elif "_BL." in name:
            bl_path = resolve_attachment(
                attachment
            )

    return si_path, bl_path


def process_email(email_id):

    # ==========================================================
    # 1. LOAD EMAIL
    # ==========================================================

    email = load_email(email_id)

    # ==========================================================
    # 2. CLASSIFY EMAIL
    # ==========================================================

    classification = classify_email(email)

    category = classification["category"]
    confidence = classification["confidence"]

    # ==========================================================
    # 3. HANDLE NON-DOCUMENT EMAILS
    # ==========================================================

    if category != "DOCUMENT_COMPARISON":

        return {
            "email_id": email_id,
            "category": category,
            "confidence": confidence,
            "status": "NOT_APPLICABLE",
            "has_defect": False,
            "defect_fields": [],
            "classification_reasons": classification[
                "reasons"
            ],
        }

    # ==========================================================
    # 4. DOCUMENT COMPARISON
    # ==========================================================

    attachments = email.get(
        "attachments",
        []
    )

    si_path, bl_path = find_si_and_bl(
        attachments
    )

    # ==========================================================
    # 5. CHECK MISSING ATTACHMENTS
    # ==========================================================

    missing = []

    if not si_path:
        missing.append("SI")

    if not bl_path:
        missing.append("BL")

    if missing:

        return {
            "email_id": email_id,
            "category": category,
            "confidence": confidence,
            "status": "NEEDS_REVIEW",
            "reason": (
                "Missing attachment(s): "
                + ", ".join(missing)
            ),
            "has_defect": False,
            "defect_fields": [],
            "classification_reasons": classification[
                "reasons"
            ],
        }

    # ==========================================================
    # 6. EXTRACT DOCUMENT TEXT
    # ==========================================================

    try:

        si_text = extract_document(
            str(si_path)
        )

        bl_text = extract_document(
            str(bl_path)
        )

    except Exception as e:

        return {
            "email_id": email_id,
            "category": category,
            "confidence": confidence,
            "status": "NEEDS_REVIEW",
            "reason": (
                f"Document extraction failed: {e}"
            ),
            "has_defect": False,
            "defect_fields": [],
            "classification_reasons": classification[
                "reasons"
            ],
        }

    # ==========================================================
    # 7. PARSE SHIPPING FIELDS
    # ==========================================================

    try:

        si_fields = parse_document(
            si_text
        )

        bl_fields = parse_document(
            bl_text
        )

    except Exception as e:

        return {
            "email_id": email_id,
            "category": category,
            "confidence": confidence,
            "status": "NEEDS_REVIEW",
            "reason": (
                f"Document parsing failed: {e}"
            ),
            "has_defect": False,
            "defect_fields": [],
            "classification_reasons": classification[
                "reasons"
            ],
        }

    # ==========================================================
    # 8. NORMALIZE
    # ==========================================================

    si_normalized = normalize_fields(
        si_fields
    )

    bl_normalized = normalize_fields(
        bl_fields
    )

    # ==========================================================
    # 9. CHECK FOR MISSING REQUIRED VALUES
    # ==========================================================

    required_fields = [
        "shipper",
        "consignee",
        "notify_party",
        "port_of_loading",
        "port_of_discharge",
        "container_count",
        "gross_weight_kg",
    ]

    missing_values = []

    for field in required_fields:

        si_value = si_normalized.get(field)
        bl_value = bl_normalized.get(field)

        if si_value is None:
            missing_values.append(
                f"SI:{field}"
            )

        if bl_value is None:
            missing_values.append(
                f"BL:{field}"
            )

    # IMPORTANT:
    # Missing/unreadable data should NOT automatically
    # become a document defect.
    if missing_values:

        return {
            "email_id": email_id,
            "category": category,
            "confidence": confidence,
            "status": "NEEDS_REVIEW",
            "reason": (
                "Required field(s) missing or "
                "could not be extracted"
            ),
            "missing_values": missing_values,
            "has_defect": False,
            "defect_fields": [],
            "si_fields": si_normalized,
            "bl_fields": bl_normalized,
            "classification_reasons": classification[
                "reasons"
            ],
        }

    # ==========================================================
    # 10. COMPARE
    # ==========================================================

    mismatches = compare_documents(
        si_normalized,
        bl_normalized
    )

    # ==========================================================
    # 11. FINAL RESULT
    # ==========================================================

    if mismatches:

        status = "DEFECT"
        has_defect = True

    else:

        status = "OK"
        has_defect = False

    return {
        "email_id": email_id,
        "category": category,
        "confidence": confidence,
        "status": status,
        "has_defect": has_defect,
        "defect_fields": mismatches,
        "si_fields": si_normalized,
        "bl_fields": bl_normalized,
        "classification_reasons": classification[
            "reasons"
        ],
    }


# ==============================================================
# COMMAND LINE TEST
# ==============================================================

if __name__ == "__main__":

    import sys

    if len(sys.argv) != 2:

        print(
            "Usage: "
            "python backend/pipeline.py <email_id>"
        )

        sys.exit(1)

    email_id = sys.argv[1]

    result = process_email(
        email_id
    )

    print("=" * 70)
    print("SHIPCHECK AI - PIPELINE RESULT")
    print("=" * 70)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )