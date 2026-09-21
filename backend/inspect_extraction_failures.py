import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
RESULTS_FILE = BASE_DIR / "output" / "pipeline_test_results.json"

if not RESULTS_FILE.exists():
    print(f"Results file not found: {RESULTS_FILE}")
    sys.exit(1)

with open(RESULTS_FILE, "r", encoding="utf-8") as f:
    results = json.load(f)

print("=" * 70)
print("SHIPCHECK AI - EXTRACTION FAILURE CASES")
print("=" * 70)

count = 0

for result in results:
    if result.get("status") != "NEEDS_REVIEW":
        continue

    reason = result.get("reason", "")

    if "extraction failed" not in reason.lower():
        continue

    count += 1

    email_id = result.get("email_id")

    print()
    print(f"Email: {email_id}")
    print(f"Reason: {reason}")
    print(f"Category: {result.get('category')}")
    print(f"Confidence: {result.get('confidence')}")

    print("Attachments:")

    email_path = BASE_DIR / "sdoc-hackathon-bundle" / "inbox" / f"{email_id}.json"

    if email_path.exists():
        try:
            with open(email_path, "r", encoding="utf-8") as ef:
                email = json.load(ef)

            attachments = email.get("attachments", [])

            if attachments:
                for attachment in attachments:
                    print(f"  - {attachment}")
            else:
                print("  NONE")
        except Exception as e:
            print(f"  Could not read email: {e}")
    else:
        print(f"  Email file not found: {email_path}")

    print("-" * 70)

print()
print("=" * 70)
print(f"TOTAL EXTRACTION FAILURE CASES: {count}")
print("=" * 70)
