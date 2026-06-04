async function initializeAdmin() {
    try {
        await loadAdminPartials();

        await loadStoreScopeOptions();

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
    document.querySelectorAll("nav button").forEach((button) => {
        button.addEventListener("click", async () => {
            document.querySelectorAll(".panel").forEach((panel) => {
                panel.classList.remove("active");
            });

            const panel = document.getElementById(button.dataset.panel);

            if (!panel) {
                showMessage(`Panel not found: ${button.dataset.panel}`);
                return;
            }

            panel.classList.add("active");

            try {
                await loadPanelData(button.dataset.panel);
            } catch (error) {
                showMessage(error.message);
                console.error(error);
            }
        });
    });
}

function bindDomainEvents() {
    if (typeof bindItemEvents === "function") {
        bindItemEvents();
    }

    if (typeof bindStoreEvents === "function") {
        bindStoreEvents();
    }

    if (typeof bindVendorEvents === "function") {
        bindVendorEvents();
    }

    if (typeof bindOrderEvents === "function") {
        bindOrderEvents();
    }
}

async function loadInitialData() {
    await loadPanelData("items-panel");

    if (typeof loadStores === "function") {
        await loadStores();
    }

    if (typeof loadVendors === "function") {
        await loadVendors();
    }

    if (typeof loadOrderFormOptions === "function") {
        await loadOrderFormOptions();
    }

    if (typeof loadOrders === "function") {
        await loadOrders();
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

});

window.addEventListener("DOMContentLoaded", initializeAdmin);