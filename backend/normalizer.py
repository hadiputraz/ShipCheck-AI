import re

PLACEHOLDER_VALUES = {
    "",
    "N/A",
    "NA",
    "N.A.",
    "N.A",
    "TBA",
    "TBC",
    "UNKNOWN",
    "UNAVAILABLE",
    "-",
    "--",
    "____",
    "_____",
    "______",
}

def is_placeholder(value):
    if value is None:
        return True

    value = str(value).strip().upper()

    if value in PLACEHOLDER_VALUES:
        return True

    # OCR placeholders such as ____MT, ____ KG, etc.
    if re.fullmatch(r"[_\-\. ]+(?:MT|KG|KGS)?", value):
        return True

    return False


def normalize_text(value):
    if value is None:
        return ""

    value = str(value).upper().strip()
    value = value.replace("×", "X")
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_party(value):
    value = normalize_text(value)

    if not value or is_placeholder(value):
        return None

    value = re.sub(
        r"^(?:SHIPPER|CONSIGNEE|NOTIFY(?:\s+PARTY)?)"
        r"\s*:\s*",
        "",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"^\([^)]*\)\s*:\s*",
        "",
        value,
    )

    value = re.sub(
        r"^PARTY\s*/\s*INTERMEDIATE\s+CONSIGNEE"
        r"\s*:\s*",
        "",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"^ON\s+BEHALF\s+OF\s+",
        "",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"^COUNT\s*:\s*",
        "",
        value,
        flags=re.IGNORECASE,
    )

    parts = re.split(r"\s*\|\s*", value)

    if parts:
        value = parts[0].strip()

    if is_placeholder(value):
        return None

    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_port(value):
    value = normalize_text(value)

    if not value or is_placeholder(value):
        return None

    value = re.sub(
        r"\s*\([A-Z]{5}\)\s*$",
        "",
        value
    )

    value = value.strip(" ,.;:")

    if is_placeholder(value):
        return None

    return value.strip()


def normalize_weight(value):
    if value is None:
        return None

    value = normalize_text(value)

    if not value or is_placeholder(value):
        return None

    value = re.sub(r"\bKGS?\b", "", value)
    value = re.sub(r"\bKILOGRAMS?\b", "", value)
    value = value.replace(",", "")
    value = value.replace(" ", "")

    # OCR placeholders such as ____MT
    if re.fullmatch(r"[_\-\.]+(?:MT|KG|KGS)?", value):
        return None

    match = re.search(r"-?\d+(?:\.\d+)?", value)

    if match:
        number_text = match.group(0)

        try:
            number = float(number_text)

            if number.is_integer():
                return int(number)

            return number

        except ValueError:
            pass

    return value


def normalize_container_count(value):
    if value is None:
        return None

    value = normalize_text(value)

    if not value or is_placeholder(value):
        return None

    value = re.sub(
        r"^COUNT\s*:\s*",
        "",
        value,
        flags=re.IGNORECASE,
    )

    value = value.replace("×", "X")
    value = re.sub(
        r"\s*X\s*",
        "X",
        value,
        flags=re.IGNORECASE,
    )

    value = value.replace(" ", "")

    if is_placeholder(value):
        return None

    return value


def normalize_field(field, value):
    if value is None:
        return None

    if field in [
        "shipper",
        "consignee",
        "notify_party",
    ]:
        return normalize_party(value)

    if field in [
        "port_of_loading",
        "port_of_discharge",
    ]:
        return normalize_port(value)

    if field == "gross_weight_kg":
        return normalize_weight(value)

    if field == "container_count":
        return normalize_container_count(value)

    value = normalize_text(value)

    if is_placeholder(value):
        return None

    return value


def normalize_fields(fields):
    normalized = {}

    for field, value in fields.items():
        normalized[field] = normalize_field(field, value)

    return normalized
