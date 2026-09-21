import json
from pathlib import Path
from collections import Counter


BASE_DIR = Path(__file__).parent.parent
RESULT_FILE = BASE_DIR / "output" / "pipeline_test_results.json"


with open(
    RESULT_FILE,
    "r",
    encoding="utf-8"
) as f:
    results = json.load(f)


reviews = [
    r for r in results
    if r.get("status") == "NEEDS_REVIEW"
]


print("=" * 70)
print("SHIPCHECK AI - NEEDS REVIEW ANALYSIS")
print("=" * 70)

print(f"Total NEEDS_REVIEW: {len(reviews)}")
print()


categories = Counter()

for result in reviews:

    reason = result.get(
        "reason",
        ""
    )

    if reason.startswith(
        "Missing attachment(s):"
    ):
        categories["Missing attachment"] += 1

    elif reason.startswith(
        "Document extraction failed:"
    ):
        categories["Extraction failed"] += 1

    elif reason.startswith(
        "Document parsing failed:"
    ):
        categories["Parsing failed"] += 1

    elif "Required field(s) missing" in reason:
        categories["Required field missing"] += 1

    else:
        categories["Other"] += 1


print("=" * 70)
print("REVIEW REASONS")
print("=" * 70)

for reason, count in categories.most_common():

    percentage = (
        count / len(reviews) * 100
    )

    print(
        f"{reason}: {count} "
        f"({percentage:.1f}%)"
    )


print()
print("=" * 70)
print("MISSING ATTACHMENT DETAILS")
print("=" * 70)


missing_attachments = Counter()

for result in reviews:

    reason = result.get(
        "reason",
        ""
    )

    if reason.startswith(
        "Missing attachment(s):"
    ):

        detail = reason.replace(
            "Missing attachment(s): ",
            ""
        )

        missing_attachments[detail] += 1


if missing_attachments:

    for detail, count in missing_attachments.most_common():

        print(
            f"{detail}: {count}"
        )

else:

    print("None")


print()
print("=" * 70)
print("MISSING REQUIRED FIELD DETAILS")
print("=" * 70)


missing_fields = Counter()

for result in reviews:

    values = result.get(
        "missing_values",
        []
    )

    for value in values:

        missing_fields[value] += 1


if missing_fields:

    for field, count in missing_fields.most_common():

        print(
            f"{field}: {count}"
        )

else:

    print("None")


print()
print("=" * 70)
print("SAMPLE REVIEW CASES")
print("=" * 70)


for result in reviews[:20]:

    print(
        f"{result.get('email_id')}: "
        f"{result.get('reason')}"
    )

    if result.get("missing_values"):

        print(
            f"  Missing: "
            f"{result['missing_values']}"
        )