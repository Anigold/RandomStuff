let loadedItems = [];
let editingItemId = null;

let itemFormStores = [];
let itemFormStoreInfos = [];

async function loadItems() {
    const scope = getSelectedStoreScope();

    const query = scope.name
        ? `?store=${encodeURIComponent(scope.name)}`
        : "";

    loadedItems = await apiRequest(`/items${query}`);

    const container = document.getElementById("items-list");

    if (!container) {
        return;
    }

    if (loadedItems.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                No items found for this store view.
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
                    ${item.subcategory ? ` · ${escapeHtml(item.subcategory)}` : ""}
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
    const createButton = document.getElementById("open-create-item-form");
    const itemForm = document.getElementById("item-form");
    const cancelButton = document.getElementById("cancel-item-edit");
    const refreshButton = document.getElementById("refresh-items");

    if (createButton) {
        createButton.addEventListener("click", async () => {
            try {
                await startCreatingItem();
            } catch (error) {
                showMessage(error.message);
                console.error(error);
            }
        });
    }

    if (itemForm) {
        itemForm.addEventListener("submit", async (event) => {
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
    }

    if (cancelButton) {
        cancelButton.addEventListener("click", closeItemFormModal);
    }

    if (refreshButton) {
        refreshButton.addEventListener("click", async () => {
            try {
                await loadItems();
            } catch (error) {
                showMessage(error.message);
                console.error(error);
            }
        });
    }
}

async function loadItemStoreAssignmentOptions(itemId = null) {
    const container = document.getElementById("item-store-assignment-fields");

    if (!container) {
        return;
    }

    itemFormStores = await apiRequest("/stores");

    itemFormStoreInfos = itemId
        ? await listItemStoreInfos(itemId)
        : [];

    const activeStores = itemFormStores.filter((store) => store.is_active);

    if (activeStores.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                No active stores found.
            </div>
        `;
        return;
    }

    const assignedStoreIds = new Set(
        itemFormStoreInfos.map((info) => info.store_id)
    );

    container.innerHTML = activeStores.map((store) => `
        <label class="checkbox-row">
            <input
                type="checkbox"
                data-item-store-assignment
                value="${escapeHtml(store.id)}"
                ${assignedStoreIds.has(store.id) ? "checked" : ""}
            />

            <span class="checkbox-row-label">
                <span class="checkbox-row-title">${escapeHtml(store.name)}</span>
                <span class="checkbox-row-meta">${escapeHtml(store.id)}</span>
            </span>
        </label>
    `).join("");
}

function getSelectedItemStoreIds() {
    return Array.from(
        document.querySelectorAll("[data-item-store-assignment]:checked")
    ).map((input) => input.value);
}

async function syncItemStoreAssignments(itemId) {
    const selectedStoreIds = new Set(getSelectedItemStoreIds());

    const existingInfosByStoreId = new Map(
        itemFormStoreInfos.map((info) => [info.store_id, info])
    );

    const existingStoreIds = new Set(existingInfosByStoreId.keys());

    const storeIdsToAdd = [...selectedStoreIds].filter(
        (storeId) => !existingStoreIds.has(storeId)
    );

    const infosToDelete = [...existingStoreIds]
        .filter((storeId) => !selectedStoreIds.has(storeId))
        .map((storeId) => existingInfosByStoreId.get(storeId));

    for (const storeId of storeIdsToAdd) {
        await createItemStoreInfo(itemId, storeId);
    }

    for (const info of infosToDelete) {
        await deleteItemStoreInfo(info.id);
    }

    itemFormStoreInfos = await listItemStoreInfos(itemId);
}
// NEED TO FINISH LOGIN AND AUTHORIZATION FOR PROPER USE
// async function listItemStoreInfos(itemId) {
//     return apiRequest(`/items/${itemId}/store-information`);
// }

// async function createItemStoreInfo(itemId, storeId) {
//     return apiRequest(`/items/${itemId}/store-information`, {
//         method: "POST",
//         body: JSON.stringify({
//             store_id: storeId,
//             is_active: true,
//         }),
//     });
// }

// async function deleteItemStoreInfo(infoId) {
//     return apiRequest(`/item-store-information/${infoId}`, {
//         method: "DELETE",
//     });
// }