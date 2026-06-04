let orderFormVendors = [];

async function loadOrderFormOptions() {
    const storeSelect = document.getElementById("order-store-select");
    const vendorSelect = document.getElementById("order-vendor-select");

    if (!storeSelect || !vendorSelect) {
        return;
    }

    const [stores, vendors] = await Promise.all([
        apiRequest("/stores"),
        apiRequest("/vendors"),
    ]);

    orderFormVendors = vendors;

    storeSelect.innerHTML = `
        <option value="">Select a store...</option>
        ${stores
            .filter((store) => store.is_active)
            .map((store) => `
                <option value="${escapeHtml(store.id)}">
                    ${escapeHtml(store.name)}
                </option>
            `)
            .join("")}
    `;

    const scope = getSelectedStoreScope();

    if (scope.id) {
        storeSelect.value = scope.id;
    }

    vendorSelect.innerHTML = `
        <option value="">Select a vendor...</option>
        ${vendors
            .filter((vendor) => vendor.is_active)
            .map((vendor) => `
                <option value="${escapeHtml(vendor.id)}">
                    ${escapeHtml(vendor.name)}
                </option>
            `)
            .join("")}
    `;

    setDefaultOrderDate();
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
        lines: [
            {
                source_item_name: data.line_source_item_name,
                source_vendor_sku: data.line_source_vendor_sku || null,
                quantity: data.line_quantity,
                unit: data.line_unit || null,
                notes: data.line_notes || "",
            },
        ],
    };
}

function bindOrderEvents() {
    const createButton = document.getElementById("open-create-order-form");
    const refreshButton = document.getElementById("refresh-orders");
    const orderForm = document.getElementById("order-form");
    const vendorSelect = document.getElementById("order-vendor-select");
    const orderDateInput = document.getElementById("order-date-input");
    const cancelButton = document.getElementById("cancel-order-create");

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

    setDefaultOrderDate();
    updateDeliveryDateFromSelectedVendor();

    openOrderFormModal();
}

function resetOrderForm() {
    const form = document.getElementById("order-form");

    if (!form) {
        return;
    }

    form.reset();
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

        document.getElementById("order-modal-title").textContent = `Order ${order.id}`;
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
    return `
        <div class="order-detail-layout">
            <div class="order-detail-summary">
                <div class="detail-grid">
                    ${isSupervisorScope() ? detailRow("Store", order.store_name || order.store_id) : ""}
                    ${detailRow("Vendor", order.vendor_name || order.vendor_id)}
                    ${detailRow("Order date", order.order_date)}
                    ${detailRow("Delivery date", order.delivery_date)}
                    ${detailRow("Status", order.status)}
                    ${detailRow("Line count", order.line_count)}
                    ${detailRow("Notes", order.notes)}
                </div>
            </div>

            <div class="order-detail-lines">
                <h4>Line Items</h4>
                ${orderLinesHtml(order.lines || [])}
            </div>

            <div class="order-detail-actions">
                <h4>Actions</h4>
                <div class="card-actions">
                    ${orderActionButtons(order)}
                </div>
            </div>
        </div>
    `;
}

function orderLinesHtml(lines) {
    if (!lines || lines.length === 0) {
        return `<p><em>No line items saved.</em></p>`;
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
                    <div>
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

    if (["fulfilled", "cancelled"].includes(status)) {
        return `
            <button onclick="deleteOrderFromModal('${escapeHtml(order.id)}')" data-variant="danger">
                Delete
            </button>
        `;
    }

    return `
        <button onclick="cancelOrderFromModal('${escapeHtml(order.id)}')">
            Cancel
        </button>
        <button onclick="markOrderExportedFromModal('${escapeHtml(order.id)}')">
            Export
        </button>
        <button onclick="markOrderFulfilledFromModal('${escapeHtml(order.id)}')">
            Fulfill
        </button>
        <button onclick="deleteOrderFromModal('${escapeHtml(order.id)}')" data-variant="danger">
            Delete
        </button>
    `;
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