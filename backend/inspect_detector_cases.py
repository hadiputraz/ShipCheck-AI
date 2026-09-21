import json
from pathlib import Path

from extractor import extract_document
from document_detector import detect_document_type

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "sdoc-hackathon-bundle"

EMAIL_IDS = [
    "email_005",
    "email_055",
    "email_059",
    "email_097",
    "email_107",
    "email_160",
    "email_171",
    "email_208",
    "email_243",
    "email_273",
    "email_291",
    "email_300",
    "email_302",
    "email_313",
    "email_351",
    "email_354",
    "email_398",
    "email_407",
    "email_411",
    "email_434",
    "email_435",
    "email_462",
    "email_481",
    "email_496",
    "email_499",
    "email_512",
    "email_513",
    "email_514",
]

def load_email(email_id):
    path = DATA_DIR / "inbox" / f"{email_id}.json"

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


for email_id in EMAIL_IDS:
    print()
    print("=" * 80)
    print(email_id)
    print("=" * 80)

    email = load_email(email_id)

    print("SUBJECT:")
    print(email.get("subject", ""))

    print()
    print("ATTACHMENTS:")

    for attachment in email.get("attachments", []):
        path = DATA_DIR / attachment

        print()
        print(f"FILE: {path.name}")

        try:
            text = extract_document(str(path))
            document_type = detect_document_type(text)

            print(f"DETECTED TYPE: {document_type}")
            print("-" * 60)

            if text:
                print(text[:1200])
            else:
                print("[NO TEXT EXTRACTED]")

        except Exception as e:
            print(f"ERROR: {e}")