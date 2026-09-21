import sys
from pathlib import Path

sys.path.insert(0, "backend")

from pipeline import load_email, resolve_attachment
from extractor import extract_document
from parser import parse_document


EMAIL_IDS = [
    "email_055",
    "email_291",
    "email_302",
    "email_354",
    "email_435",
]


for email_id in EMAIL_IDS:

    print()
    print("=" * 70)
    print(f"EMAIL: {email_id}")
    print("=" * 70)

    email = load_email(email_id)

    for attachment in email.get("attachments", []):

        filename = Path(attachment).name.upper()

        if "_BL." not in filename:
            continue

        path = resolve_attachment(attachment)

        print("Attachment:", attachment)
        print("Exists:", path.exists())

        if not path.exists():
            print("ERROR: File does not exist")
            continue

        try:
            extracted_text = extract_document(str(path))

            print("Extracted characters:", len(extracted_text or ""))

            fields = parse_document(extracted_text)

            print()
            print("PARSED FIELDS:")
            print(fields)

            print()
            print("FIELD COUNT:", len(fields))

            expected_fields = [
                "shipper",
                "consignee",
                "notify_party",
                "port_of_loading",
                "port_of_discharge",
                "container_count",
                "gross_weight_kg",
            ]

            print()
            print("MISSING FIELDS:")

            missing = []

            for field in expected_fields:
                if field not in fields:
                    missing.append(field)

            if missing:
                for field in missing:
                    print(" -", field)
            else:
                print("NONE")

        except Exception as error:

            print()
            print("ERROR:")
            print(repr(error))