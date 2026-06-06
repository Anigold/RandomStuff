
async function initializeAdmin() {
    try {
        await loadAdminPartials();

        await loadCurrentUser();
        loadStoreScopeOptions();

        applyRoleDomPermissions();
        updateScopedNavigation();

        bindNavigationEvents();
        bindStoreScopeEvents();
        bindDomainEvents();

        await loadInitialData();
    } catch (error) {
        showMessage(error.message);
        console.error(error);
    }
}

function bindNavigationEvents() {
    document.querySelectorAll("nav button[data-panel]").forEach((button) => {
        button.addEventListener("click", async () => {
            if (button.hidden) {
                return;
            }

            const panelId = button.dataset.panel;

            if (
                !canUseSupervisorSections() &&
                ["stores-panel", "vendors-panel"].includes(panelId)
            ) {
                return;
            }

            document.querySelectorAll(".panel").forEach((panel) => {
                panel.classList.remove("active");
            });

            const panel = document.getElementById(panelId);

            if (!panel) {
                return;
            }

            panel.classList.add("active");

            try {
                await loadPanelData(panelId);
            } catch (error) {
                showMessage(error.message);
                console.error(error);
            }
        });
    });
}

function bindDomainEvents() {
    if (document.getElementById("items-panel") && typeof bindItemEvents === "function") {
        bindItemEvents();
    }

    if (document.getElementById("stores-panel") && typeof bindStoreEvents === "function") {
        bindStoreEvents();
    }

    if (document.getElementById("vendors-panel") && typeof bindVendorEvents === "function") {
        bindVendorEvents();
    }

    if (document.getElementById("orders-panel") && typeof bindOrderEvents === "function") {
        bindOrderEvents();
    }
}

async function loadInitialData() {
    updateScopedNavigation();

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

async function loadPanelData(panelId) {
    if (!document.getElementById(panelId)) {
        return;
    }

    if (
        !canUseSupervisorSections() &&
        ["stores-panel", "vendors-panel"].includes(panelId)
    ) {
        return;
    }

    if (panelId === "items-panel" && typeof loadItems === "function") {
        await loadItems();
        return;
    }

    if (panelId === "stores-panel" && typeof loadStores === "function") {
        await loadStores();
        return;
    }

    if (panelId === "vendors-panel" && typeof loadVendors === "function") {
        await loadVendors();
        return;
    }

    if (panelId === "orders-panel") {
        if (typeof loadOrderFormOptions === "function") {
            await loadOrderFormOptions();
        }

        if (typeof loadOrders === "function") {
            await loadOrders();
        }
    }
}

async function loadPanelData(panelId) {
    if (
        typeof isSupervisorScope === "function" &&
        !isSupervisorScope() &&
        ["stores-panel", "vendors-panel"].includes(panelId)
    ) {
        return;
    }

    if (panelId === "items-panel" && typeof loadItems === "function") {
        await loadItems();
        return;
    }

    if (panelId === "stores-panel" && typeof loadStores === "function") {
        await loadStores();
        return;
    }

    if (panelId === "vendors-panel" && typeof loadVendors === "function") {
        await loadVendors();
        return;
    }

    if (panelId === "orders-panel") {
        if (typeof loadOrderFormOptions === "function") {
            await loadOrderFormOptions();
        }

        if (typeof loadOrders === "function") {
            await loadOrders();
        }
    }
}

document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") {
        return;
    }

    if (typeof closeItemModal === "function") {
        closeItemModal();
    }

    if (typeof closeItemFormModal === "function") {
        closeItemFormModal();
    }

    if (typeof closeVendorModal === "function") {
        closeVendorModal();
    }

    if (typeof closeVendorFormModal === "function") {
        closeVendorFormModal();
    }

    if (typeof closeOrderFormModal === "function") {
        closeOrderFormModal();
    }

    if (typeof closeOrderModal === "function") {
        closeOrderModal();
    }

    if (typeof closeOrderLineFormModal === "function") {
        closeOrderLineFormModal();
    }

});

window.addEventListener("DOMContentLoaded", initializeAdmin);


function applyRoleDomPermissions() {
    if (!canManageSetupData()) {
        removeElement("nav-stores");
        removeElement("nav-vendors");
        removeElement("stores-panel");
        removeElement("vendors-panel");
        removeElement("vendor-modal");
        removeElement("vendor-form-modal");
    }

    if (!canCreateOrders()) {
        removeElement("open-create-order-form");
        removeElement("order-form-modal");
        removeElement("order-line-form-modal");
    }

    if (!canEditItems()) {
        removeElement("open-create-item-form");
        removeElement("item-form-modal");
    }
}

function removeElement(elementId) {
    const element = document.getElementById(elementId);

    if (!element) {
        return;
    }

    element.remove();
}