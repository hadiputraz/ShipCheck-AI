import json
from pathlib import Path
from collections import Counter

from classifier import classify_email


BASE_DIR = Path(__file__).parent.parent
INBOX_DIR = BASE_DIR / "sdoc-hackathon-bundle" / "inbox"


def main():

    results = []

    files = sorted(INBOX_DIR.glob("*.json"))

    print("=" * 70)
    print("SHIPCHECK AI - DATASET CLASSIFICATION REPORT")
    print("=" * 70)

    print(f"Emails found: {len(files)}")
    print()

    # ==========================================================
    # CLASSIFY EVERY EMAIL
    # ==========================================================

    for path in files:

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                email = json.load(f)

            result = classify_email(email)

            results.append({
                "email_id": email.get(
                    "email_id",
                    path.stem
                ),
                **result
            })

        except Exception as e:

            print(
                f"ERROR: {path.name}: {e}"
            )

    # ==========================================================
    # CATEGORY DISTRIBUTION
    # ==========================================================

    categories = Counter(
        result["category"]
        for result in results
    )

    print("CATEGORY DISTRIBUTION")
    print("-" * 40)

    for category, count in categories.most_common():

        print(
            f"{category:<25} {count}"
        )

    # ==========================================================
    # CONFIDENCE DISTRIBUTION
    # ==========================================================

    print()
    print("CONFIDENCE DISTRIBUTION")
    print("-" * 40)

    confidence_ranges = {
        "0.00 - 0.49": 0,
        "0.50 - 0.69": 0,
        "0.70 - 0.84": 0,
        "0.85 - 1.00": 0,
    }

    for result in results:

        confidence = result["confidence"]

        if confidence < 0.50:

            confidence_ranges[
                "0.00 - 0.49"
            ] += 1

        elif confidence < 0.70:

            confidence_ranges[
                "0.50 - 0.69"
            ] += 1

        elif confidence < 0.85:

            confidence_ranges[
                "0.70 - 0.84"
            ] += 1

        else:

            confidence_ranges[
                "0.85 - 1.00"
            ] += 1

    for label, count in confidence_ranges.items():

        print(
            f"{label:<15} {count}"
        )

    # ==========================================================
    # LOW-CONFIDENCE EMAILS
    # ==========================================================

    print()
    print("LOW-CONFIDENCE EMAILS")
    print("-" * 40)

    low_confidence = [
        result
        for result in results
        if result["confidence"] < 0.70
    ]

    for result in low_confidence[:30]:

        print(
            f'{result["email_id"]}: '
            f'{result["category"]} '
            f'({result["confidence"]})'
        )

    if len(low_confidence) > 30:

        print(
            f"... and "
            f"{len(low_confidence) - 30} more"
        )

    # ==========================================================
    # SAVE REPORT
    # ==========================================================

    output_path = (
        BASE_DIR
        / "output"
        / "classification_report.json"
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
    print("=" * 70)
    print(
        f"Report saved to: {output_path}"
    )
    print("=" * 70)


if __name__ == "__main__":

    main()