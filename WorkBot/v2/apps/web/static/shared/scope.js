let selectedStoreScope = {
    id: null,
    name: null,
};

async function loadStoreScopeOptions() {
    const select = document.getElementById("store-scope-select");

    if (!select) {
        return;
    }

    const stores = await apiRequest("/stores");

    select.innerHTML = `
        <option value="">Supervisor</option>
        ${stores
            .filter((store) => store.is_active)
            .map((store) => `
                <option
                    value="${escapeHtml(store.id)}"
                    data-store-name="${escapeHtml(store.name)}"
                >
                    ${escapeHtml(store.name)}
                </option>
            `)
            .join("")}
    `;

    selectedStoreScope = {
        id: null,
        name: null,
    };

    updateScopedNavigation();
}

function bindStoreScopeEvents() {
    const select = document.getElementById("store-scope-select");

    if (!select) {
        return;
    }

    select.addEventListener("change", async () => {
        const selectedOption = select.options[select.selectedIndex];

        selectedStoreScope = {
            id: select.value || null,
            name: selectedOption?.dataset?.storeName || null,
        };

        try {
            updateScopedNavigation();

            await reloadActivePanel();
        } catch (error) {
            showMessage(error.message);
            console.error(error);
        }
    });
}

function getSelectedStoreScope() {
    return selectedStoreScope;
}

async function reloadActivePanel() {
    let activePanel = document.querySelector(".panel.active");

    if (
        activePanel &&
        !isSupervisorScope() &&
        ["stores-panel", "vendors-panel"].includes(activePanel.id)
    ) {
        activePanel.classList.remove("active");

        const ordersPanel = document.getElementById("orders-panel");

        if (ordersPanel) {
            ordersPanel.classList.add("active");
            activePanel = ordersPanel;
        }
    }

    if (!activePanel) {
        return;
    }

    await loadPanelData(activePanel.id);
}

function isSupervisorScope() {
    return !selectedStoreScope.id;
}

function updateScopedNavigation() {
    const supervisor = isSupervisorScope();

    setElementHidden("nav-stores", !supervisor);
    setElementHidden("nav-vendors", !supervisor);
    setElementHidden("stores-panel", !supervisor);
    setElementHidden("vendors-panel", !supervisor);

    const activePanel = document.querySelector(".panel.active");

    if (
        activePanel &&
        !supervisor &&
        ["stores-panel", "vendors-panel"].includes(activePanel.id)
    ) {
        activePanel.classList.remove("active");

        const ordersPanel = document.getElementById("orders-panel");

        if (ordersPanel) {
            ordersPanel.classList.add("active");
        }
    }
}

function setElementHidden(elementId, hidden) {
    const element = document.getElementById(elementId);

    if (!element) {
        return;
    }

    element.hidden = hidden;
}