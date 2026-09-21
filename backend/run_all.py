import json
from pathlib import Path

from pipeline import process_email


BASE_DIR = Path(__file__).parent.parent
INBOX_DIR = BASE_DIR / "sdoc-hackathon-bundle" / "inbox"
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


def main():

    email_files = sorted(
        INBOX_DIR.glob("email_*.json")
    )

    results = []

    print("=" * 70)
    print("SHIPCHECK AI - FULL DATASET TEST")
    print("=" * 70)
    print(f"Emails found: {len(email_files)}")
    print()

    for index, email_file in enumerate(
        email_files,
        start=1
    ):

        email_id = email_file.stem

        try:

            result = process_email(
                email_id
            )

        except Exception as e:

            result = {
                "email_id": email_id,
                "status": "NEEDS_REVIEW",
                "reason": f"Pipeline error: {e}",
                "has_defect": False,
                "defect_fields": [],
            }

        results.append(result)

        print(
            f"[{index}/{len(email_files)}] "
            f"{email_id}: "
            f"{result.get('status')}"
        )

    # ==========================================================
    # SAVE RESULTS
    # ==========================================================

    output_file = (
        OUTPUT_DIR /
        "pipeline_test_results.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False
        )

    # ==========================================================
    # SUMMARY
    # ==========================================================

    status_counts = {}

    category_counts = {}

    for result in results:

        status = result.get(
            "status",
            "UNKNOWN"
        )

        category = result.get(
            "category",
            "UNKNOWN"
        )

        status_counts[status] = (
            status_counts.get(status, 0) + 1
        )

        category_counts[category] = (
            category_counts.get(category, 0) + 1
        )

    print()
    print("=" * 70)
    print("STATUS DISTRIBUTION")
    print("=" * 70)

    for status, count in sorted(
        status_counts.items()
    ):

        print(
            f"{status}: {count}"
        )

    print()
    print("=" * 70)
    print("CATEGORY DISTRIBUTION")
    print("=" * 70)

    for category, count in sorted(
        category_counts.items()
    ):

        print(
            f"{category}: {count}"
        )

    print()
    print("=" * 70)
    print("RESULT SAVED")
    print("=" * 70)
    print(output_file)


if __name__ == "__main__":
    main()