async function loadHtmlPartial(path) {
    const response = await fetch(path);

    if (!response.ok) {
        throw new Error(`Could not load partial: ${path}`);
    }

    return response.text();
}

async function loadAdminPartials() {
    const sectionsContainer = document.getElementById("admin-sections");
    const modalsContainer = document.getElementById("admin-modals");

    const [
        itemsSection,
        storesSection,
        vendorsSection,
        ordersSection,

        itemDetailModal,
        itemFormModal,

        vendorDetailModal,
        vendorFormModal,

        orderDetailModal,
        orderFormModal,
        orderLineFormModal,
    ] = await Promise.all([
        loadHtmlPartial("/admin/assets/domains/items/items.html"),
        loadHtmlPartial("/admin/assets/domains/stores/stores.html"),
        loadHtmlPartial("/admin/assets/domains/vendors/vendors.html"),
        loadHtmlPartial("/admin/assets/domains/orders/orders.html"),

        loadHtmlPartial("/admin/assets/domains/items/item-detail-modal.html"),
        loadHtmlPartial("/admin/assets/domains/items/item-form-modal.html"),

        loadHtmlPartial("/admin/assets/domains/vendors/vendor-detail-modal.html"),
        loadHtmlPartial("/admin/assets/domains/vendors/vendor-form-modal.html"),

        loadHtmlPartial("/admin/assets/domains/orders/order-detail-modal.html"),
        loadHtmlPartial("/admin/assets/domains/orders/order-form-modal.html"),
        loadHtmlPartial("/admin/assets/domains/orders/order-line-form-modal.html"),
    ]);

    sectionsContainer.innerHTML = [
        itemsSection,
        storesSection,
        vendorsSection,
        ordersSection,
    ].join("");

    modalsContainer.innerHTML = [
        itemDetailModal,
        itemFormModal,
        vendorDetailModal,
        vendorFormModal,
        orderDetailModal,
        orderFormModal,
        orderLineFormModal,
    ].join("");
}