let loadedVendors = [];

async function loadVendors() {
    loadedVendors = await apiRequest("/vendors");
    const container = document.getElementById("vendors-list");

    container.innerHTML = loadedVendors.map((vendor) => `
        <button class="card compact-card" type="button" onclick="openVendorModal('${escapeHtml(vendor.id)}')">
            <h3>${escapeHtml(vendor.name)}</h3>
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

function vendorDetailsHtml(vendor) {
    return `
        <p><strong>ID:</strong> ${escapeHtml(vendor.id)}</p>
        <p><strong>Active:</strong> ${vendor.is_active}</p>

        <p><strong>Order format:</strong> ${escapeHtml(vendor.order_format)}</p>
        <p><strong>Special notes:</strong> ${escapeHtml(vendor.special_notes)}</p>

        <p><strong>Minimum order value:</strong> ${escapeHtml(vendor.min_order_value)}</p>
        <p><strong>Minimum order cases:</strong> ${escapeHtml(vendor.min_order_cases)}</p>

        <p><strong>Store IDs:</strong> ${formatList(vendor.store_ids)}</p>

        <h4>Internal Contacts</h4>
        ${formatContacts(vendor.internal_contacts)}

        <h4>Ordering</h4>
        ${formatOrdering(vendor.ordering)}

        <h4>Metadata</h4>
        <p><strong>Created at:</strong> ${escapeHtml(vendor.created_at)}</p>
        <p><strong>Updated at:</strong> ${escapeHtml(vendor.updated_at)}</p>

        <div class="card-actions">
            <button onclick="deleteVendor('${escapeHtml(vendor.id)}')">Deactivate</button>
        </div>
    `;
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
    } catch (error) {
        showMessage(error.message);
    }
}

document.getElementById("vendor-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const data = formDataToObject(event.target);

    const payload = {
        name: data.name,
        is_active: data.is_active,
        order_format: data.order_format || "",
        special_notes: data.special_notes || "",
        min_order_value: data.min_order_value || "0",
        min_order_cases: data.min_order_cases ? Number(data.min_order_cases) : 0,
        ordering: {
            email: data.ordering_email || "",
            phone_number: data.ordering_phone_number || "",
            portal_url: data.ordering_portal_url || "",
            method: [],
            schedule: [],
        },
        internal_contacts: [],
        store_ids: [],
    };

    try {
        await apiRequest("/vendors", {
            method: "POST",
            body: JSON.stringify(payload),
        });

        event.target.reset();
        event.target.elements.is_active.checked = true;

        showMessage("Vendor created.");
        await loadVendors();
        await loadOrderFormOptions();
    } catch (error) {
        showMessage(error.message);
    }
});

document.getElementById("refresh-vendors").addEventListener("click", loadVendors);

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        closeVendorModal();
    }
});