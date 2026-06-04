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
    ] = await Promise.all([
        loadHtmlPartial("/admin/domains/items/items.html"),
        loadHtmlPartial("/admin/domains/stores/stores.html"),
        loadHtmlPartial("/admin/domains/vendors/vendors.html"),
        loadHtmlPartial("/admin/domains/orders/orders.html"),

        loadHtmlPartial("/admin/domains/items/item-detail-modal.html"),
        loadHtmlPartial("/admin/domains/items/item-form-modal.html"),

        loadHtmlPartial("/admin/domains/vendors/vendor-detail-modal.html"),
        loadHtmlPartial("/admin/domains/vendors/vendor-form-modal.html"),

        loadHtmlPartial("/admin/domains/orders/order-detail-modal.html"),
        loadHtmlPartial("/admin/domains/orders/order-form-modal.html"),
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
    ].join("");
}