let selectedStoreScope = {
    id: null,
    name: null,
};

function loadStoreScopeOptions() {
    const select = document.getElementById("store-scope-select");
    const user = getCurrentUser();

    if (!select) {
        return;
    }

    if (!user) {
        select.innerHTML = `<option value="">Unknown user</option>`;
        select.disabled = true;
        return;
    }

    const stores = user.stores || [];

    if (user.can_use_supervisor_scope) {
        select.disabled = false;

        select.innerHTML = `
            <option value="">Supervisor</option>
            ${stores
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
        return;
    }

    if (stores.length === 0) {
        select.innerHTML = `<option value="">No stores assigned</option>`;
        select.disabled = true;

        selectedStoreScope = {
            id: null,
            name: null,
        };

        updateScopedNavigation();
        return;
    }

    selectedStoreScope = {
        id: stores[0].id,
        name: stores[0].name,
    };

    select.disabled = stores.length <= 1;

    select.innerHTML = stores
        .map((store, index) => `
            <option
                value="${escapeHtml(store.id)}"
                data-store-name="${escapeHtml(store.name)}"
                ${index === 0 ? "selected" : ""}
            >
                ${escapeHtml(store.name)}
            </option>
        `)
        .join("");

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

function isSupervisorScope() {
    const user = getCurrentUser();

    return Boolean(user?.can_use_supervisor_scope) && !selectedStoreScope.id;
}

function canUseSupervisorSections() {
    const user = getCurrentUser();

    return Boolean(user?.can_use_supervisor_scope) && isSupervisorScope();
}

function updateScopedNavigation() {
    const canShowSupervisorSections = canUseSupervisorSections();

    setElementHidden("nav-stores", !canShowSupervisorSections);
    setElementHidden("nav-vendors", !canShowSupervisorSections);
    setElementHidden("stores-panel", !canShowSupervisorSections);
    setElementHidden("vendors-panel", !canShowSupervisorSections);

    const activePanel = document.querySelector(".panel.active");

    if (
        activePanel &&
        !canShowSupervisorSections &&
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

async function reloadActivePanel() {
    let activePanel = document.querySelector(".panel.active");

    if (
        activePanel &&
        !canUseSupervisorSections() &&
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