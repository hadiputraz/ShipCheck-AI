import json
from pathlib import Path
from collections import Counter

from pipeline import process_email


BASE_DIR = Path(__file__).parent.parent
INBOX_DIR = BASE_DIR / "sdoc-hackathon-bundle" / "inbox"


def main():

    files = sorted(INBOX_DIR.glob("*.json"))

    results = []

    print("=" * 80)
    print("SHIPCHECK AI - FULL PIPELINE TEST")
    print("=" * 80)
    print(f"Emails found: {len(files)}")
    print()

    for index, path in enumerate(files, start=1):

        email_id = path.stem

        try:

            result = process_email(email_id)

            results.append(result)

            print(
                f"[{index:03d}/{len(files)}] "
                f"{email_id:<12} "
                f"{result.get('category', ''):<22} "
                f"{result.get('status', '')}"
            )

        except Exception as e:

            print(
                f"[{index:03d}/{len(files)}] "
                f"{email_id:<12} ERROR: {e}"
            )

    # ==========================================================
    # STATUS SUMMARY
    # ==========================================================

    print()
    print("=" * 80)
    print("STATUS DISTRIBUTION")
    print("=" * 80)

    statuses = Counter(
        result.get("status")
        for result in results
    )

    for status, count in statuses.most_common():

        print(
            f"{status:<20} {count}"
        )

    # ==========================================================
    # CATEGORY SUMMARY
    # ==========================================================

    print()
    print("=" * 80)
    print("CATEGORY DISTRIBUTION")
    print("=" * 80)

    categories = Counter(
        result.get("category")
        for result in results
    )

    for category, count in categories.most_common():

        print(
            f"{category:<25} {count}"
        )

    # ==========================================================
    # DEFECTS
    # ==========================================================

    defects = [
        result
        for result in results
        if result.get("status") == "DEFECT"
    ]

    print()
    print("=" * 80)
    print(f"DEFECT CASES: {len(defects)}")
    print("=" * 80)

    for result in defects[:50]:

        print()
        print(
            f"EMAIL: {result.get('email_id')}"
        )

        for mismatch in result.get(
            "defect_fields",
            []
        ):

            print(
                f"  FIELD: {mismatch.get('field')}"
            )

            print(
                f"    SI: {mismatch.get('si_value')}"
            )

            print(
                f"    BL: {mismatch.get('bl_value')}"
            )

    if len(defects) > 50:

        print()
        print(
            f"... and {len(defects) - 50} more defects"
        )

    # ==========================================================
    # NEEDS REVIEW
    # ==========================================================

    reviews = [
        result
        for result in results
        if result.get("status") == "NEEDS_REVIEW"
    ]

    print()
    print("=" * 80)
    print(f"NEEDS REVIEW CASES: {len(reviews)}")
    print("=" * 80)

    for result in reviews[:30]:

        print(
            f"{result.get('email_id')}: "
            f"{result.get('reason', 'No reason provided')}"
        )

    if len(reviews) > 30:

        print()
        print(
            f"... and {len(reviews) - 30} more"
        )

    # ==========================================================
    # ERRORS / UNKNOWN
    # ==========================================================

    output_path = (
        BASE_DIR
        / "output"
        / "pipeline_test_results.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("=" * 80)
    print(
        f"Full results saved to: {output_path}"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()