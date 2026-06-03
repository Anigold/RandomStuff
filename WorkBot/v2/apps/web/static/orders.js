let orderFormVendors = [];

async function loadOrderFormOptions() {
    const [stores, vendors] = await Promise.all([
        apiRequest("/stores"),
        apiRequest("/vendors"),
    ]);

    orderFormVendors = vendors;

    const storeSelect = document.getElementById("order-store-select");
    const vendorSelect = document.getElementById("order-vendor-select");

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
    const orders = await apiRequest("/orders");
    const container = document.getElementById("orders-list");

    container.innerHTML = orders.map((order) => `
        <div class="card">
            <h3>${escapeHtml(order.id)}</h3>
            <p><strong>Store:</strong> ${escapeHtml(order.store_name || order.store_id)}</p>
            <p><strong>Vendor:</strong> ${escapeHtml(order.vendor_name || order.vendor_id)}</p>
            <p><strong>Order date:</strong> ${escapeHtml(order.order_date)}</p>
            <p><strong>Delivery date:</strong> ${escapeHtml(order.delivery_date)}</p>
            <p><strong>Status:</strong> ${escapeHtml(order.status)}</p>
            <p><strong>Lines:</strong> ${order.line_count}</p>
            <div class="card-actions">
                <button onclick="cancelOrder('${order.id}')">Cancel</button>
                <button onclick="markOrderExported('${order.id}')">Export</button>
                <button onclick="markOrderFulfilled('${order.id}')">Fulfill</button>
                <button onclick="deleteOrder('${order.id}')">Delete</button>
            </div>
        </div>
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
    }
}

document.getElementById("order-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const data = formDataToObject(event.target);

    const payload = {
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

    try {
        await apiRequest("/orders", {
            method: "POST",
            body: JSON.stringify(payload),
        });

        event.target.reset();
        setDefaultOrderDate();
        updateDeliveryDateFromSelectedVendor();

        showMessage("Order created.");
        await loadOrders();
    } catch (error) {
        showMessage(error.message);
    }
});

function setDefaultOrderDate() {
    const orderDateInput = document.getElementById("order-date-input");

    if (!orderDateInput.value) {
        orderDateInput.value = formatDateForInput(new Date());
    }
}

function updateDeliveryDateFromSelectedVendor() {
    const vendorSelect = document.getElementById("order-vendor-select");
    const orderDateInput = document.getElementById("order-date-input");
    const deliveryDateInput = document.getElementById("delivery-date-input");

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

document.getElementById("refresh-orders").addEventListener("click", async () => {
    try {
        await loadOrderFormOptions();
        await loadOrders();
    } catch (error) {
        showMessage(error.message);
    }
});

document
    .getElementById("order-vendor-select")
    .addEventListener("change", updateDeliveryDateFromSelectedVendor);

document
    .getElementById("order-date-input")
    .addEventListener("change", updateDeliveryDateFromSelectedVendor);