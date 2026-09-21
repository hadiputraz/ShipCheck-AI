import re


FIELDS = [
    "shipper",
    "consignee",
    "notify_party",
    "port_of_loading",
    "port_of_discharge",
    "container_count",
    "gross_weight_kg",
]


# ==============================================================
# CLEANING
# ==============================================================

def clean_value(value):
    if not value:
        return None

    value = value.strip()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip(" |:")


def clean_label(label):
    label = label.lower().strip()

    label = re.sub(
        r"\s+",
        " ",
        label
    )

    return label


# ==============================================================
# CORE LABEL DETECTION
# ==============================================================

def contains_label(line, label):
    line_lower = clean_label(line)
    label_lower = clean_label(label)

    return label_lower in line_lower


# ==============================================================
# EXTRACT VALUE FROM PIPE/TABLE FORMAT
# ==============================================================

def extract_pipe_value(line):
    if "|" not in line:
        return None

    parts = line.split("|", 1)

    if len(parts) != 2:
        return None

    value = parts[1].strip()

    return clean_value(value)


# ==============================================================
# EXTRACT VALUE AFTER COLON
# ==============================================================

def extract_colon_value(line):
    if ":" not in line:
        return None

    parts = line.split(":", 1)

    if len(parts) != 2:
        return None

    value = parts[1].strip()

    return clean_value(value)


# ==============================================================
# FIELD-SPECIFIC LABEL DETECTION
# ==============================================================

def find_field_value(lines, field):

    # ----------------------------------------------------------
    # SHIPPER
    # ----------------------------------------------------------

    if field == "shipper":

        patterns = [
            r"\bshipper\s*/?\s*exporter\b",
            r"\bshipper\s*\(",
            r"\bshipper\b",
        ]

    # ----------------------------------------------------------
    # CONSIGNEE
    # ----------------------------------------------------------

    elif field == "consignee":

        patterns = [
            r"\bconsignee\s*\(",
            r"\bconsignee\s*\(non-negotiable\)",
            r"\bconsignee\b",
            r"\bto\s+the\s+order\s+of\b",
        ]

    # ----------------------------------------------------------
    # NOTIFY
    # ----------------------------------------------------------

    elif field == "notify_party":

        patterns = [
            r"\bnotify\s+party\b",
            r"\bnotify\b",
        ]

    # ----------------------------------------------------------
    # PORT OF LOADING
    # ----------------------------------------------------------

    elif field == "port_of_loading":

        patterns = [
            r"\bport\s+of\s+loading\b",
            r"\bload\s+port\b",
            r"\bpol\b",
        ]

    # ----------------------------------------------------------
    # PORT OF DISCHARGE
    # ----------------------------------------------------------

    elif field == "port_of_discharge":

        patterns = [
            r"\bport\s+of\s+discharge\b",
            r"\bdischarge\s+port\b",
            r"\bpod\b",
        ]

    # ----------------------------------------------------------
    # CONTAINER COUNT
    # ----------------------------------------------------------

    elif field == "container_count":

        patterns = [
            r"\bno\.\s*of\s*containers\b",
            r"\btotal\s+containers\b",
            r"\bcontainer\s+count\b",
            r"\btotal\s+container\b",
            r"\bno\.\s*of\s*containers\s+or\s+packages\b",
        ]

    # ----------------------------------------------------------
    # GROSS WEIGHT
    # ----------------------------------------------------------

    elif field == "gross_weight_kg":

        patterns = [
            r"\bgross\s+weight(?:\b|(?=[^\s]))",
            r"\bgross\s+wt(?:\b|(?=[^\s]))",
        ]

    else:
        return None

    # ==========================================================
    # SEARCH LINES
    # ==========================================================

    for i, line in enumerate(lines):

        original = line.strip()

        if not original:
            continue

        lower = original.lower()

        # ------------------------------------------------------
        # Ignore table header for gross weight
        # ------------------------------------------------------

        if field == "gross_weight_kg":

            # Total gross weight gets highest priority
            if "total" in lower and (
                "gross weight" in lower
                or "gross wt" in lower
            ):

                value = extract_pipe_value(
                    original
                )

                if value:
                    return value

                value = extract_colon_value(
                    original
                )

                if value:
                    return value

        # ------------------------------------------------------
        # Pattern matching
        # ------------------------------------------------------

        matched = False

        for pattern in patterns:

            if re.search(
                pattern,
                lower,
                re.IGNORECASE
            ):

                matched = True
                break

        if not matched:
            continue

        # ------------------------------------------------------
        # LABEL | VALUE
        # ------------------------------------------------------

        value = extract_pipe_value(
            original
        )

        if value:

            # Prevent accidentally treating a table header
            # as a real value.
            if field == "gross_weight_kg":

                if re.search(
                    r"gross\s+(weight|wt)",
                    value,
                    re.IGNORECASE
                ):

                    continue

            return value

        # ------------------------------------------------------
        # LABEL: VALUE
        # ------------------------------------------------------

        value = extract_colon_value(
            original
        )

        if value:
            return value

        # ------------------------------------------------------
        # LABEL ON ONE LINE, VALUE ON NEXT
        # ------------------------------------------------------

        if i + 1 < len(lines):

            next_line = lines[
                i + 1
            ].strip()

            if next_line:

                # Avoid using another label as the value
                if "|" not in next_line:

                    return clean_value(
                        next_line
                    )

    return None


# ==============================================================
# GROSS WEIGHT SPECIAL HANDLING
# ==============================================================

def find_gross_weight(lines):

    # ----------------------------------------------------------
    # 1. Total Gross Weight
    # ----------------------------------------------------------

    patterns = [

        r"total\s+gross\s+weight"
        r"(?:\s*\([^)]*\))*"
        r"\s*[:|]\s*([\d,.\s]+)",

        r"total\s+gross\s+wt"
        r"(?:\s*\([^)]*\))*"
        r"\s*[:|]\s*([\d,.\s]+)",
    ]

    for line in lines:

        for pattern in patterns:

            match = re.search(
                pattern,
                line,
                re.IGNORECASE
            )

            if match:

                value = match.group(1)

                value = re.sub(
                    r"\s+",
                    "",
                    value
                )

                if value:
                    return value + " KG"

    # ----------------------------------------------------------
    # 2. Gross Weight / Gross Wt
    # ----------------------------------------------------------

    value = find_field_value(
        lines,
        "gross_weight_kg"
    )

    if value:

        # Extract only numeric value
        match = re.search(
            r"[\d,]+(?:\.\d+)?",
            value
        )

        if match:

            return match.group(0) + " KG"

    return None


# ==============================================================
# PARSE DOCUMENT
# ==============================================================

def parse_document(text):

    lines = text.splitlines()

    fields = {}

    for field in FIELDS:

        if field == "gross_weight_kg":

            value = find_gross_weight(
                lines
            )

        else:

            value = find_field_value(
                lines,
                field
            )

        fields[field] = value

    return fields


# ==============================================================
# COMMAND LINE TEST
# ==============================================================

if __name__ == "__main__":

    import sys

    from extractor import extract_document

    if len(sys.argv) != 2:

        print(
            "Usage:"
        )

        print(
            "python backend/parser.py "
            "<document_path>"
        )

        sys.exit(1)

    path = sys.argv[1]

    text = extract_document(
        path
    )

    fields = parse_document(
        text
    )

    print(
        "=" * 60
    )

    print(
        "PARSED SHIPPING FIELDS"
    )

    print(
        "=" * 60
    )

    for field, value in fields.items():

        print(
            f"{field}: {value}"
        )