import json
from pathlib import Path

from classifier import classify_email


BASE_DIR = Path(__file__).parent.parent
INBOX_DIR = BASE_DIR / "sdoc-hackathon-bundle" / "inbox"


def main():

    files = sorted(INBOX_DIR.glob("*.json"))

    print("=" * 80)
    print("SHIPCHECK AI - LOW CONFIDENCE EMAIL INSPECTION")
    print("=" * 80)

    count = 0

    for path in files:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:
            email = json.load(f)

        result = classify_email(email)

        if result["confidence"] >= 0.70:
            continue

        count += 1

        print()
        print("=" * 80)
        print(f"EMAIL: {email.get('email_id')}")
        print("=" * 80)

        print()
        print("FROM:")
        print(email.get("from", ""))

        print()
        print("SUBJECT:")
        print(email.get("subject", ""))

        print()
        print("BODY:")
        print(email.get("body", ""))

        print()
        print("ATTACHMENTS:")

        attachments = email.get("attachments", [])

        if attachments:
            for attachment in attachments:
                print(f"  - {attachment}")
        else:
            print("  - None")

        print()
        print("CLASSIFIER RESULT:")
        print(f"  Category:   {result['category']}")
        print(f"  Confidence: {result['confidence']}")

        print()
        print("SCORES:")

        for category, score in result["scores"].items():
            print(f"  {category:<25} {score}")

        print()
        print("REASONS:")

        if result["reasons"]:
            for reason in result["reasons"]:
                print(f"  - {reason}")
        else:
            print("  - No indicators detected")

        if count >= 20:
            print()
            print("=" * 80)
            print("Showing first 20 low-confidence emails only.")
            print("=" * 80)
            break

    print()
    print(f"Low-confidence emails inspected: {count}")


if __name__ == "__main__":
    main()