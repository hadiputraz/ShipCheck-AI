import re

DOCUMENT_TYPES = {
    "SHIPPING_INSTRUCTION": "SHIPPING_INSTRUCTION",
    "BILL_OF_LADING": "BILL_OF_LADING",
    "COMMERCIAL_INVOICE": "COMMERCIAL_INVOICE",
    "PACKING_LIST": "PACKING_LIST",
    "CERTIFICATE_OF_ORIGIN": "CERTIFICATE_OF_ORIGIN",
    "UNKNOWN": "UNKNOWN",
}


def normalize_text(text):
    if not text:
        return ""

    text = str(text).upper()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def contains_any(text, phrases):
    return any(phrase in text for phrase in phrases)


def detect_document_type(text):
    text = normalize_text(text)

    if not text:
        return "UNKNOWN"

    # ---------------------------------------------------------
    # COMMERCIAL INVOICE
    # ---------------------------------------------------------
    if contains_any(text, [
        "COMMERCIAL INVOICE",
        "INVOICE NO.",
        "INVOICE NO:",
        "INVOICE NUMBER",
        "TOTAL AMOUNT:",
        "UNIT PRICE",
        "PAYMENT TERMS:",
        "INCOTERMS:",
    ]):
        return "COMMERCIAL_INVOICE"

    # ---------------------------------------------------------
    # CERTIFICATE OF ORIGIN
    # ---------------------------------------------------------
    if contains_any(text, [
        "CERTIFICATE OF ORIGIN",
        "CERTIFICATE OF ORIGIN NO",
        "ORIGIN CRITERION",
        "COUNTRY OF ORIGIN",
    ]):
        return "CERTIFICATE_OF_ORIGIN"

    # ---------------------------------------------------------
    # PACKING LIST
    # ---------------------------------------------------------
    if contains_any(text, [
        "PACKING LIST",
        "PACKING DETAILS",
        "PACKING LIST NO",
        "PACKAGE TYPE",
        "NUMBER OF PACKAGES",
    ]):
        return "PACKING_LIST"

    # ---------------------------------------------------------
    # BILL OF LADING
    #
    # OCR may produce:
    # BILL OF LADING
    # BILLOF LADING
    # BILL OFLADING
    # B/L
    # BL
    # ---------------------------------------------------------
    if contains_any(text, [
        "BILL OF LADING (DRAFT)",
        "DRAFT BILL OF LADING",
        "BILL OF LADING",
        "BILLOF LADING",
        "BILL OFLADING",
        "B/L NO.",
        "B/L NO:",
        "BL NO.",
        "BL NO:",
    ]):
        return "BILL_OF_LADING"

    # ---------------------------------------------------------
    # SHIPPING INSTRUCTION
    # ---------------------------------------------------------
    if contains_any(text, [
        "SHIPPING INSTRUCTION",
        "SHIPPING INSTRUCTIONS",
        "BILL OF LADING INSTRUCTION",
        "BL INSTRUCTION",
    ]):
        return "SHIPPING_INSTRUCTION"

    return "UNKNOWN"