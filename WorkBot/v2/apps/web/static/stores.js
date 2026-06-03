async function loadStores() {
    const stores = await apiRequest("/stores");
    const container = document.getElementById("stores-list");

    container.innerHTML = stores.map((store) => `
        <div class="card">
            <h3>${escapeHtml(store.name)}</h3>
            <p><strong>ID:</strong> ${escapeHtml(store.id)}</p>
            <p><strong>GM:</strong> ${escapeHtml(store.general_manager)}</p>
            <p><strong>Inventory clerk:</strong> ${escapeHtml(store.inventory_clerk)}</p>
            <p><strong>Phone:</strong> ${escapeHtml(store.phone_number)}</p>
            <p><strong>Active:</strong> ${store.is_active}</p>
            <div class="card-actions">
                <button onclick="deleteStore('${store.id}')">Deactivate</button>
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
    } catch (error) {
        showMessage(error.message);
    }
}

document.getElementById("store-form").addEventListener("submit", async (event) => {
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
    } catch (error) {
        showMessage(error.message);
    }
});

document.getElementById("refresh-stores").addEventListener("click", loadStores);