async function loadItems() {
    const items = await apiRequest("/items");
    const container = document.getElementById("items-list");

    container.innerHTML = items.map((item) => `
        <div class="card">
            <h3>${escapeHtml(item.name)}</h3>
            <p><strong>ID:</strong> ${escapeHtml(item.id)}</p>
            <p><strong>Category:</strong> ${escapeHtml(item.category)}</p>
            <p><strong>Subcategory:</strong> ${escapeHtml(item.subcategory)}</p>
            <p><strong>Active:</strong> ${item.is_active}</p>
            <div class="card-actions">
                <button onclick="deleteItem('${item.id}')">Deactivate</button>
            </div>
        </div>
    `).join("");
}

async function deleteItem(itemId) {
    try {
        await apiRequest(`/items/${itemId}`, {
            method: "DELETE",
        });
        showMessage("Item deactivated.");
        await loadItems();
    } catch (error) {
        showMessage(error.message);
    }
}

document.getElementById("item-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = formDataToObject(event.target);

    try {
        await apiRequest("/items", {
            method: "POST",
            body: JSON.stringify(payload),
        });

        event.target.reset();
        event.target.elements.is_active.checked = true;

        showMessage("Item created.");
        await loadItems();
    } catch (error) {
        showMessage(error.message);
    }
});

document.getElementById("refresh-items").addEventListener("click", loadItems);