async function loadStores() {
    const stores = await apiRequest("/stores");
    const scope = getSelectedStoreScope();
    const container = document.getElementById("stores-list");

    if (!container) {
        return;
    }

    const visibleStores = scope.id
        ? stores.filter((store) => store.id === scope.id)
        : stores;

    if (visibleStores.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                No stores found for this store view.
            </div>
        `;
        return;
    }

    container.innerHTML = visibleStores.map((store) => `
        <div class="card">
            <h3>${escapeHtml(store.name)}</h3>
            <p><strong>ID:</strong> ${escapeHtml(store.id)}</p>
            <p><strong>GM:</strong> ${escapeHtml(store.general_manager)}</p>
            <p><strong>Inventory clerk:</strong> ${escapeHtml(store.inventory_clerk)}</p>
            <p><strong>Phone:</strong> ${escapeHtml(store.phone_number)}</p>
            <p><strong>Active:</strong> ${store.is_active}</p>
            <div class="card-actions">
                <button onclick="deleteStore('${escapeHtml(store.id)}')" data-variant="danger">Deactivate</button>
            </div>
        </div>
    `).join("");
}

async function deleteStore(storeId) {
    try {
        await apiRequest(`/stores/${storeId}`, {
            method: "DELETE",
        });

        showMessage("Store deactivated.");
        await loadStores();

        if (typeof loadOrderFormOptions === "function") {
            await loadOrderFormOptions();
        }
    } catch (error) {
        showMessage(error.message);
        console.error(error);
    }
}

function bindStoreEvents() {
    const form = document.getElementById("store-form");
    const refreshButton = document.getElementById("refresh-stores");

    if (form) {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();

            const payload = formDataToObject(event.target);

            try {
                await apiRequest("/stores", {
                    method: "POST",
                    body: JSON.stringify(payload),
                });

                event.target.reset();
                event.target.elements.is_active.checked = true;

                showMessage("Store created.");
                await loadStores();

                if (typeof loadOrderFormOptions === "function") {
                    await loadOrderFormOptions();
                }
            } catch (error) {
                showMessage(error.message);
                console.error(error);
            }
        });
    }

    if (refreshButton) {
        refreshButton.addEventListener("click", loadStores);
    }
}