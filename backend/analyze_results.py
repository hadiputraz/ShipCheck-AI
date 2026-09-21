import json
import sys
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).parent.parent
RESULTS_FILE = BASE_DIR / "output" / "pipeline_test_results.json"

if not RESULTS_FILE.exists():
    print(f"Results file not found: {RESULTS_FILE}")
    sys.exit(1)

with open(RESULTS_FILE, "r", encoding="utf-8") as f:
    results = json.load(f)

actionable = [
    r for r in results
    if r.get("status") in ("OK", "DEFECT")
]

ok_results = [
    r for r in actionable
    if r.get("status") == "OK"
]

defect_results = [
    r for r in actionable
    if r.get("status") == "DEFECT"
]

print("=" * 75)
print("SHIPCHECK AI - ACTIONABLE RESULT ANALYSIS")
print("=" * 75)

print()
print(f"Total actionable cases: {len(actionable)}")
print(f"OK cases:               {len(ok_results)}")
print(f"DEFECT cases:           {len(defect_results)}")

print()
print("=" * 75)
print("DEFECT FIELD FREQUENCY")
print("=" * 75)

field_counter = Counter()

for result in defect_results:
    for defect in result.get("defect_fields", []):
        field = defect.get("field")
        if field:
            field_counter[field] += 1

if field_counter:
    for field, count in field_counter.most_common():
        print(f"{field}: {count}")
else:
    print("No defect fields found.")

print()
print("=" * 75)
print("DEFECT CASES")
print("=" * 75)

for result in defect_results:
    print()
    print(f"{result.get('email_id')}")
    print(f"  Category:   {result.get('category')}")
    print(f"  Confidence: {result.get('confidence')}")
    print(f"  Defects:")

    defects = result.get("defect_fields", [])

    if not defects:
        print("    NONE")
        continue

    for defect in defects:
        print(f"    - {defect.get('field')}")
        print(f"      SI: {defect.get('si_value')!r}")
        print(f"      BL: {defect.get('bl_value')!r}")

print()
print("=" * 75)
print("OK CASES")
print("=" * 75)

for result in ok_results:
    print(
        f"{result.get('email_id')}: "
        f"confidence={result.get('confidence')}"
    )

print()
print("=" * 75)
print("SUMMARY")
print("=" * 75)

print(f"OK:     {len(ok_results)}")
print(f"DEFECT: {len(defect_results)}")
print(f"TOTAL:  {len(actionable)}")
print("=" * 75)
