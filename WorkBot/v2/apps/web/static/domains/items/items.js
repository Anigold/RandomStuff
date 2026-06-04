let loadedItems = [];
let editingItemId = null;

async function loadItems() {
    loadedItems = await apiRequest("/items");
    const container = document.getElementById("items-list");

    if (!container) {
        return;
    }

    if (loadedItems.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                No items found.
            </div>
        `;
        return;
    }

    container.innerHTML = loadedItems.map((item) => `
        <button class="card compact-card" type="button" onclick="openItemModal('${escapeHtml(item.id)}')">
            <span class="compact-card-title">
                <h3>${escapeHtml(item.name)}</h3>
                <span class="compact-card-meta">
                    ${escapeHtml(item.category || "No category")}
                    ${item.subcategory ? ` / ${escapeHtml(item.subcategory)}` : ""}
                </span>
            </span>

            ${item.is_active
                ? `<span class="badge badge-success">Active</span>`
                : `<span class="badge badge-muted">Inactive</span>`
            }
        </button>
    `).join("");
}

function openItemModal(itemId) {
    const item = loadedItems.find((candidate) => candidate.id === itemId);

    if (!item) {
        showMessage("Item not found in loaded list.");
        return;
    }

    document.getElementById("item-modal-title").textContent = item.name;
    document.getElementById("item-modal-body").innerHTML = itemDetailsHtml(item);

    const modal = document.getElementById("item-modal");
    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
}

function closeItemModal() {
    const modal = document.getElementById("item-modal");

    if (!modal) {
        return;
    }

    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
}

function openItemFormModal() {
    const modal = document.getElementById("item-form-modal");
    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
}

function closeItemFormModal() {
    cancelItemEdit();

    const modal = document.getElementById("item-form-modal");

    if (!modal) {
        return;
    }

    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
}

function itemDetailsHtml(item) {
    return `
        <div class="detail-grid">
            ${detailRow("ID", item.id)}
            ${detailRow("Status", item.is_active ? "Active" : "Inactive")}
            ${detailRow("Name", item.name)}
            ${detailRow("Category", item.category)}
            ${detailRow("Subcategory", item.subcategory)}
        </div>

        <h4>Count Unit</h4>
        <div class="detail-grid">
            ${detailRow("Count quantity", item.count_unit_quantity)}
            ${detailRow("Count measure", item.count_unit_measure)}
            ${detailRow("Custom each name", item.custom_each_name)}
        </div>

        <h4>Each Unit</h4>
        <div class="detail-grid">
            ${detailRow("Each quantity", item.each_quantity)}
            ${detailRow("Each measure", item.each_measure)}
        </div>

        <h4>Weight</h4>
        <div class="detail-grid">
            ${detailRow("Weight quantity", item.weight_quantity)}
            ${detailRow("Weight measure", item.weight_measure)}
        </div>

        <h4>Volume</h4>
        <div class="detail-grid">
            ${detailRow("Volume quantity", item.volume_quantity)}
            ${detailRow("Volume measure", item.volume_measure)}
        </div>

        <h4>Metadata</h4>
        <div class="detail-grid">
            ${detailRow("Created at", item.created_at)}
            ${detailRow("Updated at", item.updated_at)}
        </div>

        <div class="card-actions">
            <button onclick="startEditingItem('${escapeHtml(item.id)}')" data-variant="primary">Edit</button>
            <button onclick="deleteItem('${escapeHtml(item.id)}')" data-variant="danger">Deactivate</button>
        </div>
    `;
}

function startCreatingItem() {
    editingItemId = null;
    resetItemForm();

    document.getElementById("item-form-modal-title").textContent = "Create Item";
    document.getElementById("item-submit-button").textContent = "Create Item";

    openItemFormModal();
}

function startEditingItem(itemId) {
    const item = loadedItems.find((candidate) => candidate.id === itemId);

    if (!item) {
        showMessage("Item not found in loaded list.");
        return;
    }

    editingItemId = item.id;

    resetItemForm();

    const form = document.getElementById("item-form");

    form.elements.name.value = item.name || "";
    form.elements.category.value = item.category || "";
    form.elements.subcategory.value = item.subcategory || "";
    form.elements.is_active.checked = Boolean(item.is_active);

    form.elements.count_unit_quantity.value = item.count_unit_quantity || "";
    form.elements.count_unit_measure.value = item.count_unit_measure || "";
    form.elements.custom_each_name.value = item.custom_each_name || "";

    form.elements.each_quantity.value = item.each_quantity || "";
    form.elements.each_measure.value = item.each_measure || "";

    form.elements.weight_quantity.value = item.weight_quantity || "";
    form.elements.weight_measure.value = item.weight_measure || "";

    form.elements.volume_quantity.value = item.volume_quantity || "";
    form.elements.volume_measure.value = item.volume_measure || "";

    document.getElementById("item-form-modal-title").textContent = "Edit Item";
    document.getElementById("item-submit-button").textContent = "Update Item";

    closeItemModal();
    openItemFormModal();
}

function cancelItemEdit() {
    editingItemId = null;

    const form = document.getElementById("item-form");

    if (form) {
        form.reset();
        form.elements.is_active.checked = true;
    }

    const title = document.getElementById("item-form-modal-title");
    const submitButton = document.getElementById("item-submit-button");

    if (title) {
        title.textContent = "Create Item";
    }

    if (submitButton) {
        submitButton.textContent = "Create Item";
    }
}

function resetItemForm() {
    const form = document.getElementById("item-form");

    if (!form) {
        return;
    }

    form.reset();
    form.elements.is_active.checked = true;
}

function buildItemPayload(form) {
    const data = formDataToObject(form);

    return {
        name: data.name,
        category: data.category || null,
        subcategory: data.subcategory || null,

        count_unit_quantity: data.count_unit_quantity || null,
        count_unit_measure: data.count_unit_measure || null,
        custom_each_name: data.custom_each_name || null,

        each_quantity: data.each_quantity || null,
        each_measure: data.each_measure || null,

        weight_quantity: data.weight_quantity || null,
        weight_measure: data.weight_measure || null,

        volume_quantity: data.volume_quantity || null,
        volume_measure: data.volume_measure || null,

        is_active: data.is_active,
    };
}

async function deleteItem(itemId) {
    try {
        await apiRequest(`/items/${itemId}`, {
            method: "DELETE",
        });

        closeItemModal();

        showMessage("Item deactivated.");
        await loadItems();
    } catch (error) {
        showMessage(error.message);
        console.error(error);
    }
}

function bindItemEvents() {
    document
        .getElementById("open-create-item-form")
        .addEventListener("click", startCreatingItem);

    document.getElementById("item-form").addEventListener("submit", async (event) => {
        event.preventDefault();

        try {
            const payload = buildItemPayload(event.target);

            if (editingItemId) {
                await apiRequest(`/items/${editingItemId}`, {
                    method: "PUT",
                    body: JSON.stringify(payload),
                });

                showMessage("Item updated.");
            } else {
                await apiRequest("/items", {
                    method: "POST",
                    body: JSON.stringify(payload),
                });

                showMessage("Item created.");
            }

            closeItemFormModal();
            await loadItems();
        } catch (error) {
            showMessage(error.message);
            console.error(error);
        }
    });

    document
        .getElementById("cancel-item-edit")
        .addEventListener("click", closeItemFormModal);

    document
        .getElementById("refresh-items")
        .addEventListener("click", loadItems);
}