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
print("SHIPCHECK AI - REQUIRED FIELD MISSING CASES")
print("=" * 70)

count = 0

for result in results:
    if result.get("status") != "NEEDS_REVIEW":
        continue

    missing_values = result.get("missing_values")

    if not missing_values:
        continue

    count += 1

    print()
    print(f"{result.get('email_id')}")
    print(f"Reason: {result.get('reason')}")
    print(f"Missing: {', '.join(missing_values)}")

    print("SI fields:")
    for field, value in result.get("si_fields", {}).items():
        print(f"  {field}: {value!r}")

    print("BL fields:")
    for field, value in result.get("bl_fields", {}).items():
        print(f"  {field}: {value!r}")

    print("-" * 70)

print()
print("=" * 70)
print(f"TOTAL REQUIRED FIELD CASES: {count}")
print("=" * 70)
