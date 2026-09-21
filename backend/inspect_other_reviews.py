import json

RESULT_FILE = "output/pipeline_test_results.json"

with open(RESULT_FILE, "r", encoding="utf-8") as f:
    results = json.load(f)

print("=" * 70)
print("SHIPCHECK AI - OTHER NEEDS_REVIEW CASES")
print("=" * 70)

count = 0

for result in results:
    if result.get("status") != "NEEDS_REVIEW":
        continue

    reason = result.get("reason", "")

    if reason.startswith("Missing attachment(s):"):
        continue

    if reason.startswith("Document extraction failed:"):
        continue

    if reason.startswith("Document parsing failed:"):
        continue

    if "Required field(s) missing" in reason:
        continue

    count += 1

    print(f"{result.get('email_id')}: {reason}")

print()
print("=" * 70)
print(f"TOTAL OTHER CASES: {count}")
print("=" * 70)