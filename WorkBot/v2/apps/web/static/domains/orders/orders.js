let orderFormVendors = [];
let stagedOrderLines = [];
let orderFormItems = [];

async function loadOrderFormOptions() {
    const storeSelect = document.getElementById("order-store-select");
    const vendorSelect = document.getElementById("order-vendor-select");

    if (!storeSelect || !vendorSelect) {
        return;
    }

    const user = getCurrentUser();
    const scope = getSelectedStoreScope();

    const stores = user?.stores || [];
    const vendors = await apiRequest("/vendors");

    storeSelect.innerHTML = `
        <option value="">Select a store...</option>
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

    if (scope.id) {
        storeSelect.value = scope.id;
    }

    if (!user?.can_use_supervisor_scope || stores.length <= 1) {
        storeSelect.disabled = true;
    } else {
        storeSelect.disabled = false;
    }

    vendorSelect.innerHTML = `
        <option value="">Select a vendor...</option>
        ${vendors
            .filter((vendor) => vendor.is_active)
            .map((vendor) => `
                <option
                    value="${escapeHtml(vendor.id)}"
                    data-standard-delivery-days="${escapeHtml(vendor.standard_delivery_days || "")}"
                >
                    ${escapeHtml(vendor.name)}
                </option>
            `)
            .join("")}
    `;

    await loadOrderLineItemOptions();
}

async function loadOrders() {
    const scope = getSelectedStoreScope();

    const query = scope.name
        ? `?store=${encodeURIComponent(scope.name)}`
        : "";

    const orders = await apiRequest(`/orders${query}`);
    const container = document.getElementById("orders-list");

    if (!container) {
        return;
    }

    if (orders.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                No orders found for this store view.
            </div>
        `;
        return;
    }

    container.innerHTML = orders.map((order) => `
        <button
            class="card compact-card order-card"
            type="button"
            onclick="openOrderModal('${escapeHtml(order.id)}')"
        >
            <span class="compact-card-title">
                ${isSupervisorScope()
                    ? `<span class="compact-card-meta">${escapeHtml(order.store_name || order.store_id)}</span>`
                    : ""
                }

                <h3>${escapeHtml(order.vendor_name || order.vendor_id)}</h3>

                <span class="compact-card-meta">
                    ${escapeHtml(order.order_date)} · ${escapeHtml(order.line_count)} line item${Number(order.line_count) === 1 ? "" : "s"}
                </span>
            </span>

            ${orderStatusBadge(order.status)}
        </button>
    `).join("");
}

async function cancelOrder(orderId) {
    const reason = window.prompt("Cancel reason?") || "";

    try {
        await apiRequest(`/orders/${orderId}/cancel`, {
            method: "POST",
            body: JSON.stringify({ reason }),
        });

        showMessage("Order cancelled.");
        await loadOrders();
    } catch (error) {
        showMessage(error.message);
        console.error(error);
    }
}

async function markOrderExported(orderId) {
    try {
        await apiRequest(`/orders/${orderId}/export`, {
            method: "POST",
        });

        showMessage("Order marked exported.");
        await loadOrders();
    } catch (error) {
        showMessage(error.message);
        console.error(error);
    }
}

async function markOrderFulfilled(orderId) {
    try {
        await apiRequest(`/orders/${orderId}/fulfill`, {
            method: "POST",
        });

        showMessage("Order marked fulfilled.");
        await loadOrders();
    } catch (error) {
        showMessage(error.message);
        console.error(error);
    }
}

async function deleteOrder(orderId) {
    if (!window.confirm("Hard delete this order?")) {
        return;
    }

    try {
        await apiRequest(`/orders/${orderId}`, {
            method: "DELETE",
        });

        showMessage("Order deleted.");
        await loadOrders();
    } catch (error) {
        showMessage(error.message);
        console.error(error);
    }
}

function setDefaultOrderDate() {
    const orderDateInput = document.getElementById("order-date-input");

    if (orderDateInput && !orderDateInput.value) {
        orderDateInput.value = formatDateForInput(new Date());
    }
}

function updateDeliveryDateFromSelectedVendor() {
    const vendorSelect = document.getElementById("order-vendor-select");
    const orderDateInput = document.getElementById("order-date-input");
    const deliveryDateInput = document.getElementById("delivery-date-input");

    if (!vendorSelect || !orderDateInput || !deliveryDateInput) {
        return;
    }

    const vendor = orderFormVendors.find(
        (candidate) => candidate.id === vendorSelect.value
    );

    if (!vendor || !orderDateInput.value) {
        deliveryDateInput.value = "";
        return;
    }

    const orderDate = parseDateInput(orderDateInput.value);
    const deliveryDate = getStandardDeliveryDateForVendor(vendor, orderDate);

    deliveryDateInput.value = deliveryDate
        ? formatDateForInput(deliveryDate)
        : "";
}

function getStandardDeliveryDateForVendor(vendor, orderDate) {
    const schedule = vendor.ordering?.schedule || [];

    if (schedule.length === 0) {
        return null;
    }

    const orderDayName = weekdayName(orderDate);

    const matchingEntry = schedule.find(
        (entry) => normalizeDayName(entry.order_day) === normalizeDayName(orderDayName)
    );

    if (!matchingEntry || !matchingEntry.delivery_days?.length) {
        return null;
    }

    return nextDateForWeekday(orderDate, matchingEntry.delivery_days[0]);
}

function nextDateForWeekday(startDate, targetWeekdayName) {
    const targetIndex = weekdayIndex(targetWeekdayName);

    if (targetIndex === null) {
        return null;
    }

    const result = new Date(startDate);
    const currentIndex = result.getDay();

    let daysUntilTarget = targetIndex - currentIndex;

    if (daysUntilTarget < 0) {
        daysUntilTarget += 7;
    }

    result.setDate(result.getDate() + daysUntilTarget);

    return result;
}

function weekdayName(date) {
    return [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ][date.getDay()];
}

function weekdayIndex(value) {
    const normalized = normalizeDayName(value);

    const days = {
        sunday: 0,
        monday: 1,
        tuesday: 2,
        wednesday: 3,
        thursday: 4,
        friday: 5,
        saturday: 6,
    };

    return days[normalized] ?? null;
}

function normalizeDayName(value) {
    return String(value || "").trim().toLowerCase();
}

function parseDateInput(value) {
    const [year, month, day] = value.split("-").map(Number);

    return new Date(year, month - 1, day);
}

function formatDateForInput(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");

    return `${year}-${month}-${day}`;
}

function buildOrderPayload(form) {
    const data = formDataToObject(form);

    return {
        store_id: data.store_id,
        vendor_id: data.vendor_id,
        order_date: data.order_date,
        delivery_date: data.delivery_date || null,
        notes: data.notes || "",
        lines: stagedOrderLines.map((line) => ({
            source_item_name: line.source_item_name,
            source_vendor_sku: line.source_vendor_sku || null,
            quantity: line.quantity,
            unit: line.unit || null,
            notes: line.notes || "",
        })),
    };
}

function bindOrderEvents() {
    const createButton = document.getElementById("open-create-order-form");
    const refreshButton = document.getElementById("refresh-orders");
    const orderForm = document.getElementById("order-form");
    const vendorSelect = document.getElementById("order-vendor-select");
    const orderDateInput = document.getElementById("order-date-input");
    const cancelButton = document.getElementById("cancel-order-create");
    const storeSelect = document.getElementById("order-store-select");

    const addLineButton = document.getElementById("open-add-order-line-form");
    const orderLineForm = document.getElementById("order-line-form");
    const cancelLineButton = document.getElementById("cancel-order-line-create");

    if (createButton) {
        createButton.addEventListener("click", async () => {
            try {
                await startCreatingOrder();
            } catch (error) {
                showMessage(error.message);
                console.error(error);
            }
        });
    }

    if (refreshButton) {
        refreshButton.addEventListener("click", async () => {
            try {
                await loadOrders();
            } catch (error) {
                showMessage(error.message);
                console.error(error);
            }
        });
    }

    if (vendorSelect) {
        vendorSelect.addEventListener("change", updateDeliveryDateFromSelectedVendor);
    }

    if (orderDateInput) {
        orderDateInput.addEventListener("change", updateDeliveryDateFromSelectedVendor);
    }

    if (cancelButton) {
        cancelButton.addEventListener("click", closeOrderFormModal);
    }

    if (addLineButton) {
        addLineButton.addEventListener("click", async () => {
            try {
                await openOrderLineFormModal();
            } catch (error) {
                showMessage(error.message);
                console.error(error);
            }
        });
    }

    if (cancelLineButton) {
        cancelLineButton.addEventListener("click", closeOrderLineFormModal);
    }

    if (orderLineForm) {
        orderLineForm.addEventListener("submit", (event) => {
            event.preventDefault();

            const line = buildOrderLinePayload(event.target);
            addStagedOrderLine(line);
            closeOrderLineFormModal();
        });
    }

    if (orderForm) {
        orderForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const payload = buildOrderPayload(event.target);

            try {
                await apiRequest("/orders", {
                    method: "POST",
                    body: JSON.stringify(payload),
                });

                closeOrderFormModal();

                showMessage("Order created.");
                await loadOrders();
            } catch (error) {
                showMessage(error.message);
                console.error(error);
            }
        });
    }

    if (storeSelect) {
        storeSelect.addEventListener("change", async () => {
            try {
                await loadOrderLineItemOptions();
            } catch (error) {
                showMessage(error.message);
                console.error(error);
            }
        });
    }

}

function openOrderFormModal() {
    const modal = document.getElementById("order-form-modal");

    if (!modal) {
        return;
    }

    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
}

function closeOrderFormModal() {
    resetOrderForm();

    const modal = document.getElementById("order-form-modal");

    if (!modal) {
        return;
    }

    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
}

async function startCreatingOrder() {
    resetOrderForm();

    await loadOrderFormOptions();

    const subtitle = document.querySelector("#order-form-modal .modal-subtitle");
    const scope = getSelectedStoreScope();

    if (subtitle) {
        subtitle.textContent = scope.name
            ? `Creating an order for ${scope.name}.`
            : "Enter order information and line items.";
    }




    setDefaultOrderDate();
    updateDeliveryDateFromSelectedVendor();

    openOrderFormModal();
}

function resetOrderForm() {
    const form = document.getElementById("order-form");

    if (form) {
        form.reset();
    }

    resetStagedOrderLines();
}

function orderStatusBadge(status) {
    const normalized = String(status || "").toLowerCase();

    if (["fulfilled", "processed", "exported"].includes(normalized)) {
        return `<span class="badge badge-success">${escapeHtml(status)}</span>`;
    }

    if (normalized === "pending") {
        return `<span class="badge badge-warning">${escapeHtml(status)}</span>`;
    }

    if (["cancelled", "error"].includes(normalized)) {
        return `<span class="badge badge-danger">${escapeHtml(status)}</span>`;
    }

    return `<span class="badge badge-muted">${escapeHtml(status)}</span>`;
}

async function openOrderModal(orderId) {
    try {
        const order = await apiRequest(`/orders/${orderId}`);

        document.getElementById("order-modal-title").textContent =
            order.vendor_name || order.vendor_id || "Order Details";

        document.getElementById("order-modal-subtitle").innerHTML =
            `${isSupervisorScope() ? `${escapeHtml(order.store_name || order.store_id)} · ` : ""}${escapeHtml(order.order_date)} · ${orderStatusBadge(order.status)}`;

        document.getElementById("order-modal-body").innerHTML = orderDetailsHtml(order);

        const modal = document.getElementById("order-modal");
        modal.classList.add("open");
        modal.setAttribute("aria-hidden", "false");
    } catch (error) {
        showMessage(error.message);
        console.error(error);
    }
}

function closeOrderModal() {
    const modal = document.getElementById("order-modal");

    if (!modal) {
        return;
    }

    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
}

function orderDetailsHtml(order) {
    const actionButtons = orderActionButtons(order);

    return `
        <div class="order-detail-layout">
            <div class="order-detail-summary">
                <div class="order-summary-list">
                    ${isSupervisorScope()
                        ? orderSummaryRow("Store", order.store_name || order.store_id)
                        : ""
                    }
                    ${orderSummaryRow("Vendor", order.vendor_name || order.vendor_id)}
                    ${orderSummaryRow("Order Date", order.order_date)}
                    ${orderSummaryRow("Delivery Date", order.delivery_date || "Not set")}
                    ${orderSummaryRow("Status", order.status)}
                    ${orderSummaryRow("Line Items", order.line_count)}
                    ${order.notes ? orderSummaryRow("Notes", order.notes) : ""}
                </div>
            </div>

            <div class="order-detail-lines">
                <div class="section-heading-row">
                    <h4>Line Items</h4>
                    <span class="compact-card-meta">
                        ${escapeHtml(order.line_count)} total
                    </span>
                </div>

                ${orderLinesHtml(order.lines || [])}
            </div>

            ${actionButtons
                ? `
                    <div class="order-detail-actions">
                        <div>
                            <h4>Actions</h4>
                            <p class="compact-card-meta">Update the order workflow or remove this order.</p>
                        </div>

                        <div class="card-actions">
                            ${actionButtons}
                        </div>
                    </div>
                `
                : ""
            }
        </div>
    `;
}

function orderSummaryCard(label, value) {
    return `
        <div class="summary-card">
            <div class="summary-label">${escapeHtml(label)}</div>
            <div class="summary-value">${escapeHtml(value || "")}</div>
        </div>
    `;
}

function orderLinesHtml(lines) {
    if (!lines || lines.length === 0) {
        return `<div class="empty-state">No line items saved.</div>`;
    }

    return `
        <div class="order-lines-table">
            <div class="order-lines-header">
                <div>Item</div>
                <div>SKU</div>
                <div>Qty</div>
                <div>Unit</div>
                <div>Status</div>
                <div>Notes</div>
            </div>

            ${lines.map((line) => `
                <div class="order-lines-row">
                    <div class="order-line-item-name">
                        <strong>${escapeHtml(line.item_name_snapshot || line.source_item_name || "")}</strong>
                        ${line.source_item_name && line.item_name_snapshot && line.source_item_name !== line.item_name_snapshot
                            ? `<span class="muted-text">Source: ${escapeHtml(line.source_item_name)}</span>`
                            : ""
                        }
                    </div>

                    <div>${escapeHtml(line.vendor_sku_snapshot || line.source_vendor_sku || "")}</div>
                    <div>${escapeHtml(line.quantity)}</div>
                    <div>${escapeHtml(line.unit)}</div>
                    <div>${orderStatusBadge(line.status)}</div>
                    <div>${escapeHtml(line.notes || line.status_reason || "")}</div>
                </div>
            `).join("")}
        </div>
    `;
}

function orderActionButtons(order) {
    const status = String(order.status || "").toLowerCase();

    if (!canModifyOrders()) {
        return "";
    }

    const buttons = [];

    if (!["fulfilled", "cancelled"].includes(status)) {
        buttons.push(`
            <button onclick="cancelOrderFromModal('${escapeHtml(order.id)}')">
                Cancel
            </button>
        `);
    }

    if (canUseSupervisorOrderActions()) {
        if (!["fulfilled", "cancelled"].includes(status)) {
            buttons.push(`
                <button onclick="markOrderExportedFromModal('${escapeHtml(order.id)}')">
                    Export
                </button>
                <button onclick="markOrderFulfilledFromModal('${escapeHtml(order.id)}')">
                    Fulfill
                </button>
            `);
        }

        buttons.push(`
            <button onclick="deleteOrderFromModal('${escapeHtml(order.id)}')" data-variant="danger">
                Delete
            </button>
        `);
    }

    return buttons.join("");
}

async function cancelOrderFromModal(orderId) {
    await cancelOrder(orderId);
    closeOrderModal();
}

async function markOrderExportedFromModal(orderId) {
    await markOrderExported(orderId);
    closeOrderModal();
}

async function markOrderFulfilledFromModal(orderId) {
    await markOrderFulfilled(orderId);
    closeOrderModal();
}

async function deleteOrderFromModal(orderId) {
    await deleteOrder(orderId);
    closeOrderModal();
}

async function openOrderLineFormModal() {
    const modal = document.getElementById("order-line-form-modal");

    if (!modal) {
        return;
    }

    const form = document.getElementById("order-line-form");

    if (form) {
        form.reset();
    }

    await loadOrderLineItemOptions();

    modal.classList.add("open");
    modal.setAttribute("aria-hidden", "false");
}

function closeOrderLineFormModal() {
    const modal = document.getElementById("order-line-form-modal");

    if (!modal) {
        return;
    }

    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
}

function addStagedOrderLine(line) {
    stagedOrderLines.push({
        id: crypto.randomUUID ? crypto.randomUUID() : String(Date.now()),
        ...line,
    });

    renderStagedOrderLines();
}

function removeStagedOrderLine(lineId) {
    stagedOrderLines = stagedOrderLines.filter((line) => line.id !== lineId);
    renderStagedOrderLines();
}

function renderStagedOrderLines() {
    const container = document.getElementById("staged-order-lines-list");

    if (!container) {
        return;
    }

    if (stagedOrderLines.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                No line items added yet.
            </div>
        `;
        return;
    }

    container.innerHTML = stagedOrderLines.map((line, index) => `
        <div class="staged-order-line-card">
            <div class="staged-order-line-header">
                <div>
                    <h4>Line ${index + 1}</h4>
                    <p class="compact-card-meta">${escapeHtml(line.source_item_name)}</p>
                </div>

                <button type="button" onclick="removeStagedOrderLine('${escapeHtml(line.id)}')" data-variant="danger">
                    Remove
                </button>
            </div>

            <div class="detail-grid">
                ${detailRow("Vendor SKU", line.source_vendor_sku)}
                ${detailRow("Quantity", line.quantity)}
                ${detailRow("Unit", line.unit)}
                ${detailRow("Notes", line.notes)}
            </div>
        </div>
    `).join("");
}

function resetStagedOrderLines() {
    stagedOrderLines = [];
    renderStagedOrderLines();
}

function buildOrderLinePayload(form) {
    const data = formDataToObject(form);

    return {
        source_item_name: data.source_item_name,
        source_vendor_sku: data.source_vendor_sku || null,
        quantity: data.quantity,
        unit: data.unit || null,
        notes: data.notes || "",
    };
}

async function loadOrderLineItemOptions() {
    const itemSelect = document.getElementById("order-line-item-select");
    const storeSelect = document.getElementById("order-store-select");

    if (!itemSelect || !storeSelect) {
        return;
    }

    const selectedStoreOption = storeSelect.options[storeSelect.selectedIndex];
    const storeName = selectedStoreOption?.dataset?.storeName || "";

    if (!storeName) {
        orderFormItems = [];
        itemSelect.innerHTML = `
            <option value="">Select a store first...</option>
        `;
        return;
    }

    orderFormItems = await apiRequest(
        `/items?store=${encodeURIComponent(storeName)}&include_inactive=false`
    );

    if (orderFormItems.length === 0) {
        itemSelect.innerHTML = `
            <option value="">No items available for this store</option>
        `;
        return;
    }

    itemSelect.innerHTML = `
        <option value="">Select an item...</option>
        ${orderFormItems
            .map((item) => `
                <option value="${escapeHtml(item.name)}" data-item-id="${escapeHtml(item.id)}">
                    ${escapeHtml(item.name)}
                </option>
            `)
            .join("")}
    `;
}