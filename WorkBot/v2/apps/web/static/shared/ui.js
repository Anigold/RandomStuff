function showMessage(message) {
    const element = document.getElementById("message");
    element.textContent = message;
    element.classList.add("visible");

    window.setTimeout(() => {
        element.classList.remove("visible");
    }, 3000);
}

function formDataToObject(form) {
    const data = new FormData(form);
    const result = {};

    for (const [key, value] of data.entries()) {
        if (value === "") {
            continue;
        }

        result[key] = value;
    }

    for (const checkbox of form.querySelectorAll("input[type='checkbox']")) {
        result[checkbox.name] = checkbox.checked;
    }

    return result;
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function detailRow(label, value) {
    return `
        <div class="detail-row">
            <div class="detail-label">${escapeHtml(label)}</div>
            <div class="detail-value">${escapeHtml(value || "")}</div>
        </div>
    `;
}