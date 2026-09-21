import re


def normalize_text(value):
    if value is None:
        return ""

    value = str(value).upper().strip()
    value = value.replace("×", "X")
    value = re.sub(r"\s+", " ", value)

    return value


def normalize_party(value):
    value = normalize_text(value)

    # Remove labels such as:
    # NOTIFY:
    # NOTIFY PARTY:
    # SHIPPER:
    # CONSIGNEE:
    value = re.sub(
        r"^(SHIPPER|CONSIGNEE|NOTIFY(?: PARTY)?)\s*:\s*",
        "",
        value
    )

    # Keep the principal/company name.
    # Ignore address information after "|"
    parts = re.split(r"\s*\|\s*", value)

    if parts:
        value = parts[0].strip()

    # Remove "ON BEHALF OF" when it appears before the company name
    value = re.sub(r"^ON BEHALF OF\s+", "", value)

    return value.strip()


def normalize_port(value):
    value = normalize_text(value)

    # Remove UN/LOCODE in parentheses.
    #
    # SINGAPORE (SGSIN)
    # -> SINGAPORE
    #
    # PYEONGTAEK, SOUTH KOREA (KRPTK)
    # -> PYEONGTAEK, SOUTH KOREA
    value = re.sub(r"\s*\([A-Z]{5}\)\s*$", "", value)

    return value.strip()


def normalize_weight(value):
    value = normalize_text(value)

    value = re.sub(r"\bKGS?\b", "", value)

    value = value.replace(",", "")
    value = value.replace(" ", "")

    return value


def normalize_container_count(value):
    value = normalize_text(value)

    value = re.sub(r"\s*X\s*", "X", value)
    value = value.replace(" ", "")

    return value


def values_match(field, si_value, bl_value):

    if field in [
        "shipper",
        "consignee",
        "notify_party"
    ]:
        return normalize_party(si_value) == normalize_party(bl_value)

    if field in [
        "port_of_loading",
        "port_of_discharge"
    ]:
        return normalize_port(si_value) == normalize_port(bl_value)

    if field == "gross_weight_kg":
        return normalize_weight(si_value) == normalize_weight(bl_value)

    if field == "container_count":
        return normalize_container_count(si_value) == normalize_container_count(bl_value)

    return normalize_text(si_value) == normalize_text(bl_value)


def compare_documents(si_fields, bl_fields):

    mismatches = []

    fields = [
        "shipper",
        "consignee",
        "notify_party",
        "port_of_loading",
        "port_of_discharge",
        "container_count",
        "gross_weight_kg"
    ]

    for field in fields:

        si_value = si_fields.get(field)
        bl_value = bl_fields.get(field)

        if not values_match(field, si_value, bl_value):

            mismatches.append({
                "field": field,
                "si_value": si_value,
                "bl_value": bl_value
            })

    return mismatches


# Backwards-compatible alias
compare_fields = compare_documents


if __name__ == "__main__":

    si = {
        "shipper": "APRIL FINE PAPER TRADING | 77 ROBINSON ROAD",
        "consignee": "NOTIFY: CLIFFORD PAPER INC",
        "notify_party": "CLIFFORD PAPER INC",
        "port_of_loading": "SINGAPORE",
        "port_of_discharge": "PYEONGTAEK, SOUTH KOREA",
        "container_count": "12X20'FCL",
        "gross_weight_kg": 243588
    }

    bl = {
        "shipper": "APRIL FINE PAPER TRADING",
        "consignee": "CLIFFORD PAPER INC",
        "notify_party": "CLIFFORD PAPER INC",
        "port_of_loading": "SINGAPORE (SGSIN)",
        "port_of_discharge": "PYEONGTAEK, SOUTH KOREA (KRPTK)",
        "container_count": "12X20'FCL",
        "gross_weight_kg": 243588
    }

    mismatches = compare_documents(si, bl)

    print("TEST RESULT:")

    if not mismatches:
        print("NO MISMATCH DETECTED")
    else:
        for mismatch in mismatches:
            print(mismatch)