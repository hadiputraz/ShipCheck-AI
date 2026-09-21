const API_URL = "http://127.0.0.1:8000";

const analyzeBtn = document.getElementById("analyzeBtn");
const emailIdInput = document.getElementById("emailId");

const loading = document.getElementById("loading");
const result = document.getElementById("result");
const error = document.getElementById("error");
const errorText = document.getElementById("errorText");

const statusCard = document.getElementById("statusCard");
const statusIcon = document.getElementById("statusIcon");
const statusTitle = document.getElementById("statusTitle");
const statusDescription = document.getElementById("statusDescription");

const category = document.getElementById("category");
const confidence = document.getElementById("confidence");
const siType = document.getElementById("siType");
const blType = document.getElementById("blType");

const mismatchSection = document.getElementById("mismatchSection");
const mismatchList = document.getElementById("mismatchList");

const fieldsTable = document.getElementById("fieldsTable");

const reviewReason = document.getElementById("reviewReason");
const reviewText = document.getElementById("reviewText");


const FIELD_LABELS = {
    shipper: "Shipper",
    consignee: "Consignee",
    notify_party: "Notify Party",
    port_of_loading: "Port of Loading",
    port_of_discharge: "Port of Discharge",
    container_count: "Container Count",
    gross_weight_kg: "Gross Weight (kg)"
};


analyzeBtn.addEventListener("click", analyzeEmail);


emailIdInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        analyzeEmail();
    }
});


async function analyzeEmail() {

    const emailId = emailIdInput.value.trim();

    if (!emailId) {
        showError("Please enter an email ID.");
        return;
    }

    setLoading(true);

    try {

        const response = await fetch(`${API_URL}/analyze`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email_id: emailId
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "The API returned an error."
            );
        }

        renderResult(data);

    } catch (err) {

        showError(
            `Could not connect to ShipCheck AI API. ${err.message}`
        );

    } finally {

        setLoading(false);
    }
}


function renderResult(data) {

    result.classList.remove("hidden");
    error.classList.add("hidden");

    category.textContent =
        formatCategory(data.category);

    confidence.textContent =
        data.confidence !== undefined
            ? `${Math.round(data.confidence * 100)}%`
            : "-";

    const documentTypes = data.document_types || {};

    siType.textContent =
        formatDocumentType(documentTypes.SI);

    blType.textContent =
        formatDocumentType(documentTypes.BL);

    renderStatus(data);

    renderMismatches(data);

    renderFields(data);

    renderReviewReason(data);
}


function renderStatus(data) {

    statusCard.classList.remove(
        "defect",
        "review"
    );

    if (data.status === "OK") {

        statusIcon.textContent = "✓";
        statusTitle.textContent =
            "No Mismatch Detected";

        statusDescription.textContent =
            "All 7 required fields match between the SI and Draft BL.";

        return;
    }

    if (data.status === "DEFECT") {

        statusCard.classList.add("defect");

        statusIcon.textContent = "!";
        statusTitle.textContent =
            "Defect Detected";

        const count =
            (data.defect_fields || []).length;

        statusDescription.textContent =
            `${count} field${count === 1 ? "" : "s"} do not match.`;

        return;
    }

    if (data.status === "NEEDS_REVIEW") {

        statusCard.classList.add("review");

        statusIcon.textContent = "?";
        statusTitle.textContent =
            "Human Review Required";

        statusDescription.textContent =
            "ShipCheck AI could not safely complete the comparison.";

        return;
    }

    statusIcon.textContent = "?";
    statusTitle.textContent =
        data.status || "Unknown Result";

    statusDescription.textContent =
        "Please review the analysis result.";
}


function renderMismatches(data) {

    mismatchList.innerHTML = "";

    const mismatches =
        data.defect_fields || [];

    if (
        data.status !== "DEFECT" ||
        mismatches.length === 0
    ) {

        mismatchSection.classList.add("hidden");
        return;
    }

    mismatchSection.classList.remove("hidden");

    mismatches.forEach(function(item) {

        const box =
            document.createElement("div");

        box.className = "mismatch-box";

        const field =
            FIELD_LABELS[item.field] ||
            item.field;

        box.innerHTML = `
            <div class="mismatch-field">
                ${escapeHtml(field)}
            </div>

            <div class="mismatch-values">
                <strong>SI:</strong>
                ${escapeHtml(formatValue(item.si_value))}
                <br>

                <strong>Draft BL:</strong>
                ${escapeHtml(formatValue(item.bl_value))}
            </div>
        `;

        mismatchList.appendChild(box);
    });
}


function renderFields(data) {

    fieldsTable.innerHTML = "";

    if (
        !data.si_fields ||
        !data.bl_fields
    ) {
        document.getElementById(
            "fieldsSection"
        ).classList.add("hidden");

        return;
    }

    document.getElementById(
        "fieldsSection"
    ).classList.remove("hidden");

    Object.keys(FIELD_LABELS).forEach(function(field) {

        const siValue =
            data.si_fields[field];

        const blValue =
            data.bl_fields[field];

        const isMatch =
            JSON.stringify(siValue) ===
            JSON.stringify(blValue);

        const row =
            document.createElement("tr");

        row.innerHTML = `
            <td>
                <strong>${escapeHtml(FIELD_LABELS[field])}</strong>
            </td>

            <td>
                ${escapeHtml(formatValue(siValue))}
            </td>

            <td>
                ${escapeHtml(formatValue(blValue))}
            </td>

            <td class="${isMatch ? "match" : "mismatch"}">
                ${isMatch ? "✓ Match" : "✗ Mismatch"}
            </td>
        `;

        fieldsTable.appendChild(row);
    });
}


function renderReviewReason(data) {

    if (
        data.status !== "NEEDS_REVIEW"
    ) {

        reviewReason.classList.add("hidden");
        return;
    }

    reviewReason.classList.remove("hidden");

    let text =
        data.reason ||
        "The document comparison requires human review.";

    if (
        Array.isArray(data.missing_values) &&
        data.missing_values.length
    ) {

        text +=
            ` Missing: ${data.missing_values.join(", ")}.`;
    }

    reviewText.textContent = text;
}


function setLoading(isLoading) {

    if (isLoading) {

        loading.classList.remove("hidden");
        result.classList.add("hidden");
        error.classList.add("hidden");

        analyzeBtn.disabled = true;
        analyzeBtn.textContent = "Analyzing...";

    } else {

        loading.classList.add("hidden");

        analyzeBtn.disabled = false;
        analyzeBtn.textContent = "Analyze";
    }
}


function showError(message) {

    result.classList.add("hidden");
    error.classList.remove("hidden");

    errorText.textContent = message;
}


function formatCategory(value) {

    if (!value) {
        return "-";
    }

    return value
        .replaceAll("_", " ")
        .replace(/\b\w/g, c => c.toUpperCase());
}


function formatDocumentType(value) {

    if (!value) {
        return "-";
    }

    return value
        .replaceAll("_", " ")
        .replace(/\b\w/g, c => c.toUpperCase());
}


function formatValue(value) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "Not available";
    }

    return String(value);
}


function escapeHtml(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}
