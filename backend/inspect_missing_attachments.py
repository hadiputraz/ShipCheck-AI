import json
from pathlib import Path

from pipeline import load_email
from classifier import classify_email


BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "sdoc-hackathon-bundle"


def main():

    print("=" * 70)
    print("SHIPCHECK AI - ATTACHMENT RESOLUTION ANALYSIS")
    print("=" * 70)

    document_comparison_count = 0
    missing_count = 0

    for i in range(1, 521):

        email_id = f"email_{i:03d}"

        email = load_email(email_id)
        classification = classify_email(email)

        if classification["category"] != "DOCUMENT_COMPARISON":
            continue

        document_comparison_count += 1

        attachments = email.get("attachments", [])

        has_si = False
        has_bl = False

        for attachment in attachments:

            filename = Path(attachment).name.upper()

            if "_SI." in filename:
                has_si = True

            if "_BL." in filename:
                has_bl = True

        if not has_si or not has_bl:

            missing_count += 1

            print()
            print("-" * 70)
            print(email_id)
            print("Subject:", email.get("subject", ""))
            print("Attachments:")

            if attachments:
                for attachment in attachments:
                    print("  ", attachment)
            else:
                print("   NONE")

            print("Detected SI:", has_si)
            print("Detected BL:", has_bl)

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("Document comparison emails:", document_comparison_count)
    print("Currently missing SI/BL:", missing_count)


if __name__ == "__main__":
    main()