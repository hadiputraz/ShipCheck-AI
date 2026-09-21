import sys

sys.path.insert(0, "backend")

from pipeline import load_email, find_si_and_bl
from extractor import extract_document


IDS = [
    "email_107",
    "email_171",
    "email_243",
    "email_496",
    "email_513",
    "email_516",
    "email_518",
    "email_519",
    "email_520",
]


for email_id in IDS:

    print()
    print("=" * 80)
    print(email_id)
    print("=" * 80)

    email = load_email(email_id)

    si_path, bl_path = find_si_and_bl(
        email.get("attachments", [])
    )

    print()
    print("===== SI =====")

    if si_path:
        try:
            print(
                extract_document(
                    str(si_path)
                )
            )
        except Exception as e:
            print("SI EXTRACTION ERROR:", e)
    else:
        print("SI NOT FOUND")

    print()
    print("===== BL =====")

    if bl_path:
        try:
            print(
                extract_document(
                    str(bl_path)
                )
            )
        except Exception as e:
            print("BL EXTRACTION ERROR:", e)
    else:
        print("BL NOT FOUND")