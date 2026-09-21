import re


# ============================================================
# Helpers
# ============================================================

def clean_value(value):
    """
    Clean extracted field values.

    Treat common blank / unavailable values as missing.
    """
    if value is None:
        return None

    value = str(value).strip()

    # Normalize whitespace
    value = re.sub(r"\s+", " ", value)

    # Remove common OCR punctuation around N/A
    cleaned = re.sub(r"[\s\.\-_:;|/\\]+", "", value.upper())

    # Treat these as missing
    if cleaned in {
        "",
        "N/A",
        "NA",
        "NONE",
        "NULL",
        "NOTAVAILABLE",
        "NOTPROVIDED",
        "UNKNOWN",
        "BLANK",
        "NIL",
        "N/A.",
    }:
        return None

    # Additional direct checks
    if value.upper() in {
        "N/A",
        "N/A.",
        "NA",
        "NONE",
        "NULL",
        "NOT AVAILABLE",
        "NOT PROVIDED",
        "UNKNOWN",
        "NIL",
    }:
        return None

    return value.strip()


def normalize_label(label):
    """
    Normalize a field label for easier matching.
    """
    if not label:
        return ""

    label = str(label).upper().strip()

    # Normalize common separators
    label = label.replace("×", "X")

    # Collapse whitespace
    label = re.sub(r"\s+", " ", label)

    return label.strip()


def split_pipe_line(line):
    """
    Split a line such as:

        SHIPPER | ABC COMPANY

    into:

        ("SHIPPER", "ABC COMPANY")

    Returns (None, None) if no pipe exists.
    """
    if "|" not in line:
        return None, None

    label, value = line.split("|", 1)

    label = normalize_label(label)
    value = clean_value(value)

    return label, value


def first_match(text, patterns, flags=re.IGNORECASE | re.MULTILINE):
    """
    Return the first regex capture group that matches.

    Patterns should use [ \\t] instead of \\s when matching
    spaces on the same line, to avoid accidentally crossing
    into the next document line.
    """
    for pattern in patterns:
        match = re.search(pattern, text, flags)
        if match:
            value = clean_value(match.group(1))
            if value is not None:
                return value

    return None


# ============================================================
# Pipe-based parser
# ============================================================

def parse_pipe_lines(text):
    """
    Parse documents where fields are commonly represented as:

        LABEL | VALUE

    Supports normal, bilingual and OCR-style labels.
    """

    fields = {}

    if not text:
        return fields

    lines = str(text).splitlines()

    for line in lines:

        line = line.strip()

        if not line or "|" not in line:
            continue

        label, value = split_pipe_line(line)

        if not label or value is None:
            continue

        # ----------------------------------------------------
        # SHIPPER
        # ----------------------------------------------------

        if (
            label.startswith("SHIPPER")
            or label.startswith("SHIPPER/EXPORTER")
        ):
            fields["shipper"] = value
            continue

        # ----------------------------------------------------
        # CONSIGNEE
        # ----------------------------------------------------

        if (
            label.startswith("CONSIGNEE")
            or label.startswith("TO THE ORDER OF")
        ):
            fields["consignee"] = value
            continue

        # ----------------------------------------------------
        # NOTIFY PARTY
        # ----------------------------------------------------

        if (
            label.startswith("NOTIFY")
            or label.startswith("PARTY / INTERMEDIATE CONSIGNEE")
            or label.startswith("PARTY/INTERMEDIATE CONSIGNEE")
            or "INTERMEDIATE CONSIGNEE" in label
        ):
            fields["notify_party"] = value
            continue

        # ----------------------------------------------------
        # PORT OF LOADING
        # ----------------------------------------------------

        if (
            "PORT OF LOADING" in label
            or "PORT OF LEADING" in label
            or "PORTOT" in label
            or "PORTOF" in label
            or label == "POL"
            or label.startswith("POL ")
            or label == "LOAD PORT"
            or label.startswith("LOAD PORT ")
        ):
            fields["port_of_loading"] = value
            continue

        # ----------------------------------------------------
        # PORT OF DISCHARGE
        # ----------------------------------------------------

        if (
            "PORT OF DISCHARGE" in label
            or "PORTOF DISCHARGE" in label
            or label == "POD"
            or label.startswith("POD ")
            or label == "DISCHARGE PORT"
            or label.startswith("DISCHARGE PORT ")
        ):
            fields["port_of_discharge"] = value
            continue

        # ----------------------------------------------------
        # CONTAINER COUNT
        # ----------------------------------------------------

        if (
            "TOTAL CONTAINERS" in label
            or "CONTAINER COUNT" in label
            or "NO OF CONTAINERS" in label
            or "NO. OF CONTAINERS" in label
            or "CONTAINERS OR PACKAGES" in label
            or label == "CONTAINERS"
            or label.startswith("CONTAINERS ")
            or label == "COUNT"
            or label.startswith("COUNT ")
        ):
            fields["container_count"] = value
            continue

        # ----------------------------------------------------
        # GROSS WEIGHT
        # ----------------------------------------------------

        if (
            "GROSS WEIGHT" in label
            or "GROSS WT" in label
            or "GROSS Wt" in label
        ):
            fields["gross_weight_kg"] = value
            continue

    return fields


# ============================================================
# Regex-based parser
# ============================================================

def parse_regex_fields(text):
    """
    Parse documents without pipe separators.

    All same-line whitespace is matched using [ \\t] so that
    a field cannot accidentally consume the next document line.
    """

    fields = {}

    if not text:
        return fields

    text = str(text)

    # --------------------------------------------------------
    # SHIPPER
    # --------------------------------------------------------

    shipper = first_match(
        text,
        [
            r"^\s*SHIPPER/EXPORTER[ \t]*:[ \t]*(.+)$",
            r"^\s*SHIPPER[ \t]*:[ \t]*(.+)$",
            r"^\s*SHIPPER\s*\(PRINCIPAL OR SELLER\)[ \t]*:[ \t]*(.+)$",
        ],
    )

    if shipper is not None:
        fields["shipper"] = shipper

    # --------------------------------------------------------
    # CONSIGNEE
    # --------------------------------------------------------

    consignee = first_match(
        text,
        [
            r"^\s*CONSIGNEE\s*\(NON-NEGOTIABLE\)[ \t]*:[ \t]*(.+)$",
            r"^\s*CONSIGNEE[ \t]*:[ \t]*(.+)$",
            r"^\s*TO THE ORDER OF[ \t]*:[ \t]*(.+)$",
        ],
    )

    if consignee is not None:
        fields["consignee"] = consignee

    # --------------------------------------------------------
    # NOTIFY PARTY
    # --------------------------------------------------------

    notify = first_match(
        text,
        [
            r"^\s*NOTIFY PARTY[ \t]*:[ \t]*(.+)$",
            r"^\s*NOTIFY[ \t]*:[ \t]*(.+)$",
            r"^\s*NOTIFY PARTY/INTERMEDIATE CONSIGNEE[ \t]*:[ \t]*(.+)$",
            r"^\s*NOTIFY PARTY\s*/\s*INTERMEDIATE CONSIGNEE[ \t]*:[ \t]*(.+)$",
        ],
    )

    if notify is not None:
        fields["notify_party"] = notify

    # --------------------------------------------------------
    # PORT OF LOADING
    # --------------------------------------------------------

    pol = first_match(
        text,
        [
            r"^\s*PORT OF LOADING[ \t]*\([^)]*\)[ \t]*:[ \t]*(.+)$",
            r"^\s*PORT OF LOADING[ \t]*:[ \t]*(.+)$",
            r"^\s*PORT OF LEADING[ \t]*:[ \t]*(.+)$",
            r"^\s*POL[ \t]*\([^)]*\)[ \t]*:[ \t]*(.+)$",
            r"^\s*POL[ \t]*:[ \t]*(.+)$",
            r"^\s*LOAD PORT[ \t]*\([^)]*\)[ \t]*:[ \t]*(.+)$",
            r"^\s*LOAD PORT[ \t]*:[ \t]*(.+)$",
        ],
    )

    if pol is not None:
        fields["port_of_loading"] = pol

    # --------------------------------------------------------
    # PORT OF DISCHARGE
    # --------------------------------------------------------

    pod = first_match(
        text,
        [
            r"^\s*PORT OF DISCHARGE[ \t]*\([^)]*\)[ \t]*:[ \t]*(.+)$",
            r"^\s*PORT OF DISCHARGE[ \t]*:[ \t]*(.+)$",
            r"^\s*DISCHARGE PORT[ \t]*\([^)]*\)[ \t]*:[ \t]*(.+)$",
            r"^\s*DISCHARGE PORT[ \t]*:[ \t]*(.+)$",
            r"^\s*POD[ \t]*\([^)]*\)[ \t]*:[ \t]*(.+)$",
            r"^\s*POD[ \t]*:[ \t]*(.+)$",
        ],
    )

    if pod is not None:
        fields["port_of_discharge"] = pod

    # --------------------------------------------------------
    # CONTAINER COUNT
    # --------------------------------------------------------

    container_count = first_match(
        text,
        [
            r"^\s*NO\.\s*OF\s*CONTAINERS\s*OR\s*PACKAGES[ \t]*:[ \t]*(.+)$",
            r"^\s*NO\.\s*OF\s*CONTAINERS[ \t]*:[ \t]*(.+)$",
            r"^\s*NO\s*OF\s*CONTAINERS[ \t]*:[ \t]*(.+)$",
            r"^\s*TOTAL\s*CONTAINERS[ \t]*:[ \t]*(.+)$",
            r"^\s*CONTAINER\s*COUNT[ \t]*:[ \t]*(.+)$",
            r"^\s*CONTAINERS[ \t]*:[ \t]*(.+)$",
        ],
    )

    if container_count is not None:
        fields["container_count"] = container_count

    # --------------------------------------------------------
    # GROSS WEIGHT
    # --------------------------------------------------------

    gross_weight = first_match(
        text,
        [
            r"^\s*GROSS\s*WEIGHT\s*\(KG\)[ \t]*:[ \t]*(.+)$",
            r"^\s*GROSS\s*WEIGHT\s*\(KGS\)[ \t]*:[ \t]*(.+)$",
            r"^\s*GROSS\s*WEIGHT[ \t]*:[ \t]*(.+)$",
            r"^\s*GROSS\s*WT\s*\(KGS\)[ \t]*:[ \t]*(.+)$",
            r"^\s*GROSS\s*WT\s*\(KG\)[ \t]*:[ \t]*(.+)$",
            r"^\s*GROSS\s*WT[ \t]*:[ \t]*(.+)$",
            r"^\s*GROSS\s*WEIGHT.*?\(KGS\)[ \t]*:[ \t]*(.+)$",
        ],
    )

    if gross_weight is not None:
        fields["gross_weight_kg"] = gross_weight

    return fields


# ============================================================
# Main parser
# ============================================================

def parse_document(text):
    """
    Parse a Shipping Instruction or Bill of Lading.

    Strategy:
        1. Try pipe-separated fields.
        2. Try regex-based fields.
        3. Merge both results.

    Pipe parsing takes priority because the dataset frequently
    contains structured spreadsheet/DOCX extraction in the
    form LABEL | VALUE.
    """

    if not text:
        return {}

    pipe_fields = parse_pipe_lines(text)
    regex_fields = parse_regex_fields(text)

    fields = {}

    # Add regex fields first
    fields.update(regex_fields)

    # Pipe fields override regex fields
    fields.update(pipe_fields)

    return fields