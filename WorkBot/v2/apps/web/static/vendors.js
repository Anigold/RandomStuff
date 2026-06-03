let loadedVendors = [];
let editingVendorId = null;

async function loadVendors() {
    loadedVendors = await apiRequest("/vendors");
    const container = document.getElementById("vendors-list");

    if (loadedVendors.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                No vendors found.
            </div>
        `;
        return;
    }

    container.innerHTML = loadedVendors.map((vendor) => `
        <button class="card compact-card" type="button" onclick="openVendorModal('${escapeHtml(vendor.id)}')">
            <span class="compact-card-title">
                <h3>${escapeHtml(vendor.name)}</h3>
                <span class="compact-card-meta">${escapeHtml(vendor.order_format || "No order format")}</span>
            </span>

            ${vendor.is_active
                ? `<span class="badge badge-success">Active</span>`
                : `<span class="badge badge-muted">Inactive</span>`
            }
        </button>
    `).join("");
}

function openVendorModal(vendorId) {
    const vendor = loadedVendors.find((candidate) => candidate.id === vendorId);

    if (!vendor) {
        showMessage("Vendor not found in loaded list.");
        return;
    }

    document.getElementById("vendor-modal-title").textContent = vendor.name;
    document.getElementById("vendor-modal-body").innerHTML = vendorDetailsHtml(vendor);

    const modal = document.getElementById("vendor-modal");
    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
}

function closeVendorModal() {
    const modal = document.getElementById("vendor-modal");
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
}

function openVendorFormModal() {
    const modal = document.getElementById("vendor-form-modal");
    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
}

function closeVendorFormModal() {
    cancelVendorEdit();

    const modal = document.getElementById("vendor-form-modal");
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
}

function vendorDetailsHtml(vendor) {
    return `
        <div class="detail-grid">
            ${detailRow("ID", vendor.id)}
            ${detailRow("Status", vendor.is_active ? "Active" : "Inactive")}
            ${detailRow("Order format", vendor.order_format)}
            ${detailRow("Special notes", vendor.special_notes)}
            ${detailRow("Minimum order value", vendor.min_order_value)}
            ${detailRow("Minimum order cases", vendor.min_order_cases)}
        </div>

        <h4>Store References</h4>
        ${formatStoreReferences(vendor.store_references)}

        <h4>Internal Contacts</h4>
        ${formatContacts(vendor.internal_contacts)}

        <h4>Ordering</h4>
        ${formatOrdering(vendor.ordering)}

        <h4>Metadata</h4>
        <div class="detail-grid">
            ${detailRow("Created at", vendor.created_at)}
            ${detailRow("Updated at", vendor.updated_at)}
        </div>

        <div class="card-actions">
            <button onclick="startEditingVendor('${escapeHtml(vendor.id)}')" data-variant="primary">Edit</button>
            <button onclick="deleteVendor('${escapeHtml(vendor.id)}')" data-variant="danger">Deactivate</button>
        </div>
    `;
}

function detailRow(label, value) {
    return `
        <div class="detail-row">
            <div class="detail-label">${escapeHtml(label)}</div>
            <div class="detail-value">${escapeHtml(value || "")}</div>
        </div>
    `;
}

function startCreatingVendor() {
    editingVendorId = null;
    resetVendorForm();

    document.getElementById("vendor-form-modal-title").textContent = "Create Vendor";
    document.getElementById("vendor-submit-button").textContent = "Create Vendor";

    openVendorFormModal();
}

function startEditingVendor(vendorId) {
    const vendor = loadedVendors.find((candidate) => candidate.id === vendorId);

    if (!vendor) {
        showMessage("Vendor not found in loaded list.");
        return;
    }

    editingVendorId = vendor.id;

    resetVendorForm();

    const form = document.getElementById("vendor-form");

    form.elements.name.value = vendor.name || "";
    form.elements.order_format.value = vendor.order_format || "";
    form.elements.special_notes.value = vendor.special_notes || "";
    form.elements.min_order_value.value = vendor.min_order_value || "0";
    form.elements.min_order_cases.value = vendor.min_order_cases || 0;
    form.elements.is_active.checked = Boolean(vendor.is_active);

    form.elements.ordering_email.value = vendor.ordering?.email || "";
    form.elements.ordering_phone_number.value = vendor.ordering?.phone_number || "";
    form.elements.ordering_portal_url.value = vendor.ordering?.portal_url || "";
    form.elements.ordering_methods.value = (vendor.ordering?.method || []).join(", ");

    clearRepeatableFields();

    (vendor.internal_contacts || []).forEach((contact) => {
        addVendorContactRow(contact);
    });

    (vendor.ordering?.schedule || []).forEach((entry) => {
        addVendorScheduleRow(entry);
    });

    (vendor.store_references || []).forEach((reference) => {
        addVendorStoreReferenceRow(reference);
    });

    document.getElementById("vendor-form-modal-title").textContent = "Edit Vendor";
    document.getElementById("vendor-submit-button").textContent = "Update Vendor";

    closeVendorModal();
    openVendorFormModal();
}

function cancelVendorEdit() {
    editingVendorId = null;
    resetVendorForm();

    document.getElementById("vendor-form-modal-title").textContent = "Create Vendor";
    document.getElementById("vendor-submit-button").textContent = "Create Vendor";
}

function resetVendorForm() {
    const form = document.getElementById("vendor-form");

    form.reset();
    form.elements.is_active.checked = true;

    clearRepeatableFields();
}

function clearRepeatableFields() {
    document.getElementById("vendor-contacts-fields").innerHTML = "";
    document.getElementById("vendor-schedule-fields").innerHTML = "";
    document.getElementById("vendor-store-reference-fields").innerHTML = "";
}

function addVendorContactRow(contact = {}) {
    const container = document.getElementById("vendor-contacts-fields");
    const row = document.createElement("div");

    row.className = "repeatable-row";
    row.innerHTML = `
        <label>
            Name
            <input data-contact-field="name" value="${escapeHtml(contact.name || "")}" />
        </label>

        <label>
            Title
            <input data-contact-field="title" value="${escapeHtml(contact.title || "")}" />
        </label>

        <label>
            Email
            <input data-contact-field="email" value="${escapeHtml(contact.email || "")}" />
        </label>

        <label>
            Phone
            <input data-contact-field="phone" value="${escapeHtml(contact.phone || "")}" />
        </label>

        <button type="button" onclick="removeRepeatableRow(this)">Remove</button>
    `;

    container.appendChild(row);
}

function addVendorScheduleRow(entry = {}) {
    const container = document.getElementById("vendor-schedule-fields");
    const row = document.createElement("div");

    row.className = "repeatable-row";
    row.innerHTML = `
        <label>
            Order Day
            <input data-schedule-field="order_day" placeholder="Monday" value="${escapeHtml(entry.order_day || "")}" />
        </label>

        <label>
            Delivery Days
            <input data-schedule-field="delivery_days" placeholder="Wednesday, Friday" value="${escapeHtml((entry.delivery_days || []).join(", "))}" />
        </label>

        <label>
            Cutoff Time
            <input data-schedule-field="cutoff_time" placeholder="14:00" value="${escapeHtml(entry.cutoff_time || "")}" />
        </label>

        <button type="button" onclick="removeRepeatableRow(this)">Remove</button>
    `;

    container.appendChild(row);
}

function addVendorStoreReferenceRow(reference = {}) {
    const container = document.getElementById("vendor-store-reference-fields");
    const row = document.createElement("div");

    row.className = "repeatable-row";
    row.innerHTML = `
        <label>
            Store ID
            <input data-store-reference-field="store_id" value="${escapeHtml(reference.store_id || "")}" />
        </label>

        <label>
            Vendor Store Reference
            <input data-store-reference-field="vendor_store_reference" value="${escapeHtml(reference.vendor_store_reference || "")}" />
        </label>

        <button type="button" onclick="removeRepeatableRow(this)">Remove</button>
    `;

    container.appendChild(row);
}

function removeRepeatableRow(button) {
    button.closest(".repeatable-row").remove();
}

function buildVendorPayload(form) {
    const data = formDataToObject(form);

    return {
        name: data.name,
        is_active: data.is_active,
        order_format: data.order_format || "",
        special_notes: data.special_notes || "",
        min_order_value: data.min_order_value || "0",
        min_order_cases: data.min_order_cases ? Number(data.min_order_cases) : 0,
        internal_contacts: collectVendorContacts(),
        ordering: {
            method: splitCommaList(data.ordering_methods),
            email: data.ordering_email || "",
            phone_number: data.ordering_phone_number || "",
            portal_url: data.ordering_portal_url || "",
            schedule: collectVendorSchedule(),
        },
        store_references: collectVendorStoreReferences(),
    };
}

function collectVendorContacts() {
    return Array.from(document.querySelectorAll("#vendor-contacts-fields .repeatable-row"))
        .map((row) => ({
            name: getRepeatableValue(row, "contact", "name"),
            title: getRepeatableValue(row, "contact", "title"),
            email: getRepeatableValue(row, "contact", "email"),
            phone: getRepeatableValue(row, "contact", "phone"),
        }))
        .filter((contact) => contact.name);
}

function collectVendorSchedule() {
    return Array.from(document.querySelectorAll("#vendor-schedule-fields .repeatable-row"))
        .map((row) => ({
            order_day: getRepeatableValue(row, "schedule", "order_day"),
            delivery_days: splitCommaList(
                getRepeatableValue(row, "schedule", "delivery_days")
            ),
            cutoff_time: getRepeatableValue(row, "schedule", "cutoff_time"),
        }))
        .filter((entry) => entry.order_day);
}

function collectVendorStoreReferences() {
    return Array.from(document.querySelectorAll("#vendor-store-reference-fields .repeatable-row"))
        .map((row) => ({
            store_id: getRepeatableValue(row, "store-reference", "store_id"),
            vendor_store_reference: getRepeatableValue(
                row,
                "store-reference",
                "vendor_store_reference"
            ),
        }))
        .filter((reference) => reference.store_id);
}

function getRepeatableValue(row, group, field) {
    const input = row.querySelector(`[data-${group}-field="${field}"]`);

    return input ? input.value.trim() : "";
}

function splitCommaList(value) {
    return String(value || "")
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean);
}

function formatContacts(contacts) {
    if (!contacts || contacts.length === 0) {
        return `<p><em>No contacts saved.</em></p>`;
    }

    return `
        <div class="nested-list">
            ${contacts.map((contact) => `
                <div class="nested-card">
                    <p><strong>Name:</strong> ${escapeHtml(contact.name)}</p>
                    <p><strong>Title:</strong> ${escapeHtml(contact.title)}</p>
                    <p><strong>Email:</strong> ${escapeHtml(contact.email)}</p>
                    <p><strong>Phone:</strong> ${escapeHtml(contact.phone)}</p>
                </div>
            `).join("")}
        </div>
    `;
}

function formatOrdering(ordering) {
    if (!ordering) {
        return `<p><em>No ordering info saved.</em></p>`;
    }

    return `
        <div class="nested-card">
            <p><strong>Methods:</strong> ${formatList(ordering.method)}</p>
            <p><strong>Email:</strong> ${escapeHtml(ordering.email)}</p>
            <p><strong>Portal URL:</strong> ${escapeHtml(ordering.portal_url)}</p>
            <p><strong>Phone number:</strong> ${escapeHtml(ordering.phone_number)}</p>

            <h5>Schedule</h5>
            ${formatSchedule(ordering.schedule)}
        </div>
    `;
}

function formatSchedule(schedule) {
    if (!schedule || schedule.length === 0) {
        return `<p><em>No schedule saved.</em></p>`;
    }

    return `
        <div class="nested-list">
            ${schedule.map((entry) => `
                <div class="nested-card">
                    <p><strong>Order day:</strong> ${escapeHtml(entry.order_day)}</p>
                    <p><strong>Delivery days:</strong> ${formatList(entry.delivery_days)}</p>
                    <p><strong>Cutoff time:</strong> ${escapeHtml(entry.cutoff_time)}</p>
                </div>
            `).join("")}
        </div>
    `;
}

function formatStoreReferences(storeReferences) {
    if (!storeReferences || storeReferences.length === 0) {
        return `<p><em>No store references saved.</em></p>`;
    }

    return `
        <div class="nested-list">
            ${storeReferences.map((reference) => `
                <div class="nested-card">
                    <p><strong>Store ID:</strong> ${escapeHtml(reference.store_id)}</p>
                    <p><strong>Vendor reference:</strong> ${escapeHtml(reference.vendor_store_reference || "None")}</p>
                </div>
            `).join("")}
        </div>
    `;
}

function formatList(values) {
    if (!values || values.length === 0) {
        return `<em>None</em>`;
    }

    return values.map((value) => escapeHtml(value)).join(", ");
}

async function deleteVendor(vendorId) {
    try {
        await apiRequest(`/vendors/${vendorId}`, {
            method: "DELETE",
        });

        closeVendorModal();

        showMessage("Vendor deactivated.");
        await loadVendors();

        if (typeof loadOrderFormOptions === "function") {
            await loadOrderFormOptions();
        }
    } catch (error) {
        showMessage(error.message);
    }
}

document.getElementById("open-create-vendor-form").addEventListener("click", startCreatingVendor);

document.getElementById("vendor-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    try {
        const payload = buildVendorPayload(event.target);

        if (editingVendorId) {
            await apiRequest(`/vendors/${editingVendorId}`, {
                method: "PUT",
                body: JSON.stringify(payload),
            });

            showMessage("Vendor updated.");
        } else {
            await apiRequest("/vendors", {
                method: "POST",
                body: JSON.stringify(payload),
            });

            showMessage("Vendor created.");
        }

        closeVendorFormModal();

        await loadVendors();

        if (typeof loadOrderFormOptions === "function") {
            await loadOrderFormOptions();
        }
    } catch (error) {
        showMessage(error.message);
    }
});

document.getElementById("cancel-vendor-edit").addEventListener("click", closeVendorFormModal);

document.getElementById("add-vendor-contact").addEventListener("click", () => {
    addVendorContactRow();
});

document.getElementById("add-vendor-schedule").addEventListener("click", () => {
    addVendorScheduleRow();
});

document.getElementById("add-vendor-store-reference").addEventListener("click", () => {
    addVendorStoreReferenceRow();
});

document.getElementById("refresh-vendors").addEventListener("click", loadVendors);

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        closeVendorModal();
        closeVendorFormModal();
    }
});