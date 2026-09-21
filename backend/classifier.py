import re


CATEGORIES = [
    "DOCUMENT_COMPARISON",
    "NEW_SI_REQUEST",
    "INVOICE_QUERY",
    "GENERAL",
    "SPAM",
]


def normalize_text(text):
    if not text:
        return ""

    return re.sub(r"\s+", " ", text.lower()).strip()


def classify_email(email):
    subject = normalize_text(email.get("subject", ""))
    body = normalize_text(email.get("body", ""))

    attachments = email.get("attachments", [])

    attachment_names = " ".join(
        normalize_text(str(a))
        for a in attachments
    )

    combined = " ".join([
        subject,
        body,
        attachment_names
    ])

    scores = {
        "DOCUMENT_COMPARISON": 0,
        "NEW_SI_REQUEST": 0,
        "INVOICE_QUERY": 0,
        "GENERAL": 0,
        "SPAM": 0,
    }

    reasons = []

    # ==========================================================
    # DOCUMENT COMPARISON
    # ==========================================================

    comparison_terms = [
        "draft bl",
        "draft b/l",
        "bill of lading",
        "compare",
        "check the details",
        "confirm docs",
        "confirm documents",
        "si and bl",
        "si & bl",
        "shipping instruction",
    ]

    for term in comparison_terms:
        if term in combined:
            scores["DOCUMENT_COMPARISON"] += 2
            reasons.append(
                f"comparison indicator: {term}"
            )

    # Detect SI attachment
    has_si = any(
        re.search(
            r"(^|[_\-/])si([_.\-]|$)",
            str(a).lower()
        )
        for a in attachments
    )

    # Detect BL attachment
    has_bl = any(
        re.search(
            r"(^|[_\-/])bl([_.\-]|$)",
            str(a).lower()
        )
        for a in attachments
    )

    if has_si:
        scores["DOCUMENT_COMPARISON"] += 3
        reasons.append("SI attachment detected")

    if has_bl:
        scores["DOCUMENT_COMPARISON"] += 3
        reasons.append("BL attachment detected")

    if has_si and has_bl:
        scores["DOCUMENT_COMPARISON"] += 5
        reasons.append(
            "both SI and BL attachments detected"
        )

    # ==========================================================
    # NEW SI REQUEST
    # ==========================================================

    new_si_terms = [
        "new shipping instruction",
        "new si",
        "send si",
        "please send the si",
        "provide si",
        "submit si",
        "shipping instruction required",
        "shipping instruction request",
    ]

    for term in new_si_terms:
        if term in combined:
            scores["NEW_SI_REQUEST"] += 4
            reasons.append(
                f"new SI indicator: {term}"
            )

    # ==========================================================
    # INVOICE QUERY
    # ==========================================================

    invoice_terms = [
        "invoice",
        "invoicing",
        "billing",
        "bill us",
        "payment",
        "payment status",
        "invoice number",
        "invoice query",
    ]

    for term in invoice_terms:
        if term in combined:
            scores["INVOICE_QUERY"] += 3
            reasons.append(
                f"invoice indicator: {term}"
            )

    # ==========================================================
    # SPAM
    # ==========================================================

    spam_terms = [
        "unsubscribe",
        "winner",
        "lottery",
        "prize",
        "congratulations",
        "free money",
        "click here",
        "casino",
        "crypto investment",
        "make money fast",
    ]

    for term in spam_terms:
        if term in combined:
            scores["SPAM"] += 5
            reasons.append(
                f"spam indicator: {term}"
            )

    # ==========================================================
    # CATEGORY DECISION
    # ==========================================================

    # If both SI and BL are attached, this is strongly
    # indicative of a document-comparison request.
    if has_si and has_bl:
        category = "DOCUMENT_COMPARISON"
    else:
        category = max(
            scores,
            key=scores.get
        )

    highest_score = scores[category]

    # ==========================================================
    # CONFIDENCE
    # ==========================================================

    if category == "DOCUMENT_COMPARISON":

        if has_si and has_bl:
            confidence = 0.98

        elif highest_score >= 6:
            confidence = 0.85

        elif highest_score >= 4:
            confidence = 0.70

        elif highest_score >= 2:
            confidence = 0.55

        else:
            confidence = 0.30

    elif category == "INVOICE_QUERY":

        if highest_score >= 6:
            confidence = 0.90

        elif highest_score >= 3:
            confidence = 0.70

        else:
            confidence = 0.40

    elif category == "NEW_SI_REQUEST":

        if highest_score >= 8:
            confidence = 0.90

        elif highest_score >= 4:
            confidence = 0.70

        else:
            confidence = 0.40

    elif category == "SPAM":

        if highest_score >= 10:
            confidence = 0.95

        elif highest_score >= 5:
            confidence = 0.75

        else:
            confidence = 0.40

    else:
        confidence = 0.30

    # No meaningful indicators
    if highest_score == 0:
        category = "GENERAL"
        confidence = 0.30

    # ==========================================================
    # RESULT
    # ==========================================================

    return {
        "category": category,
        "confidence": confidence,
        "scores": scores,
        "reasons": reasons,
    }


# ==============================================================
# COMMAND LINE TEST
# ==============================================================

if __name__ == "__main__":

    import json
    import sys

    if len(sys.argv) != 2:
        print(
            "Usage: python backend/classifier.py <email_json>"
        )
        sys.exit(1)

    path = sys.argv[1]

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        email = json.load(f)

    result = classify_email(email)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )