import sys
from pathlib import Path

sys.path.insert(0, "backend")

from pipeline import load_email, resolve_attachment
from extractor import extract_document


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

    attachments = email.get("attachments", [])

    print("Attachments:")
    for attachment in attachments:
        print("  ", attachment)

    bl_found = False

    for attachment in attachments:

        filename = Path(attachment).name.upper()

        if "_BL." not in filename:
            continue

        bl_found = True

        path = resolve_attachment(attachment)

        print()
        print("-" * 70)
        print("BL ATTACHMENT")
        print("-" * 70)

        print("Attachment:", attachment)
        print("Path:", path)
        print("Exists:", path.exists())

        if not path.exists():
            continue

        try:

            extracted_text = extract_document(str(path))

            print("Extracted length:", len(extracted_text or ""))

            print()
            print("EXTRACTED TEXT:")
            print("-" * 70)

            if extracted_text:
                print(extracted_text[:5000])
            else:
                print("[EMPTY EXTRACTION]")

            print("-" * 70)

        except Exception as error:

            print()
            print("EXTRACTION ERROR:")
            print(repr(error))

    if not bl_found:
        print()
        print("NO BL ATTACHMENT FOUND")