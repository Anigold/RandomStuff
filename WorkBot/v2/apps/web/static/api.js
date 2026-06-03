const API_BASE = "/api";

function showMessage(message) {
    const element = document.getElementById("message");
    element.textContent = message;
    element.classList.add("visible");

    window.setTimeout(() => {
        element.classList.remove("visible");
    }, 3000);
}

async function apiRequest(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
        ...options,
    });

    if (!response.ok) {
        let detail = `${response.status} ${response.statusText}`;

        try {
            const error = await response.json();
            detail = error.detail || detail;
        } catch {
            // Ignore non-JSON error responses.
        }

        throw new Error(detail);
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
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

document.querySelectorAll("nav button").forEach((button) => {
    button.addEventListener("click", async () => {
        document.querySelectorAll(".panel").forEach((panel) => {
            panel.classList.remove("active");
        });

        document.getElementById(button.dataset.panel).classList.add("active");

        try {
            if (button.dataset.panel === "items-panel") {
                await loadItems();
            }

            if (button.dataset.panel === "stores-panel") {
                await loadStores();
            }

            if (button.dataset.panel === "vendors-panel") {
                await loadVendors();
            }

            if (button.dataset.panel === "orders-panel") {
                await loadOrderFormOptions();
                await loadOrders();
            }
        } catch (error) {
            showMessage(error.message);
        }
    });
});

window.addEventListener("DOMContentLoaded", async () => {
    try {
        await loadItems();
        await loadStores();
        await loadVendors();
        await loadOrderFormOptions();
        await loadOrders();
    } catch (error) {
        showMessage(error.message);
    }
});