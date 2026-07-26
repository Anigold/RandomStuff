import { useState } from "react";

import {
  cancelOrder,
  createOrder,
  getOrder,
  type OrderDto,
  type OrderWriteDto,
} from "../../../api/ordersApi";
import { useAccessToken } from "../../auth/hooks/useAccessTokens";
import { useStoreScope } from "../../stores/hooks/useStoreScope";
import { OrderActionsModal } from "../components/OrderActionsModal";
import { OrderFormModal } from "../components/OrderFormModal";
import { OrdersTable } from "../components/OrdersTable";
import { useOrderFormOptions } from "../hooks/useOrderFormOptions";
import { useOrders } from "../hooks/useOrders";

export function OrdersPage() {
  const accessToken = useAccessToken();
  const { activeScopeId } = useStoreScope();
  const { orders, isLoadingOrders, orderErrorMessage, reloadOrders } =
    useOrders();

  const {
    stores,
    vendors,
    isLoadingOptions,
    optionsErrorMessage,
    defaultStoreId,
    requireStoreSelection,
    reloadOptions,
  } = useOrderFormOptions();

  const [selectedOrder, setSelectedOrder] = useState<OrderDto | null>(null);
  const [isLoadingOrderDetail, setIsLoadingOrderDetail] = useState(false);
  const [isCreatingOrder, setIsCreatingOrder] = useState(false);
  const [actionErrorMessage, setActionErrorMessage] = useState<string | null>(
    null,
  );

  async function handleSelectOrder(order: OrderDto) {
    if (!activeScopeId) {
      setActionErrorMessage("Select an operating scope before opening an order.");
      return;
    }

    setActionErrorMessage(null);
    setSelectedOrder(null);
    setIsCreatingOrder(false);
    setIsLoadingOrderDetail(true);

    try {
      const orderDetail = await getOrder({
        accessToken,
        scopeId: activeScopeId,
        orderId: order.id,
      });

      setSelectedOrder(orderDetail);
    } catch (error) {
      setActionErrorMessage(
        error instanceof Error ? error.message : "Unable to load order details.",
      );
    } finally {
      setIsLoadingOrderDetail(false);
    }
  }

  async function handleCreateOrder(order: OrderWriteDto) {
    if (!activeScopeId) {
      throw new Error("Select an operating scope before creating an order.");
    }

    await createOrder({
      accessToken,
      scopeId: activeScopeId,
      order,
    });

    await Promise.all([reloadOrders(), reloadOptions()]);
    setIsCreatingOrder(false);
  }

  async function handleCancelOrder(order: OrderDto) {
    if (!activeScopeId) {
      setActionErrorMessage(
        "Select an operating scope before cancelling an order.",
      );
      return;
    }

    const reason = window.prompt(
      "Cancel this order? Optionally enter a cancellation reason.",
      "",
    );

    if (reason === null) {
      return;
    }

    setActionErrorMessage(null);

    try {
      await cancelOrder({
        accessToken,
        scopeId: activeScopeId,
        orderId: order.id,
        reason: reason.trim() || null,
      });

      await reloadOrders();
      setSelectedOrder(null);
    } catch (error) {
      setActionErrorMessage(
        error instanceof Error ? error.message : "Unable to cancel order.",
      );
    }
  }

  const canOpenCreateOrder =
    !isLoadingOptions &&
    !optionsErrorMessage &&
    vendors.some((vendor) => vendor.is_active) &&
    (!requireStoreSelection || stores.length > 0);

  return (
    <section className="page-stack">
      <header className="page-header">
        <div>
          <h2>Orders</h2>
          <p>Review and manage scoped purchasing orders.</p>
        </div>

        <button
          type="button"
          disabled={!canOpenCreateOrder}
          title={
            canOpenCreateOrder
              ? undefined
              : "Order options are still loading or unavailable."
          }
          onClick={() => {
            setActionErrorMessage(null);
            setSelectedOrder(null);
            setIsCreatingOrder(true);
          }}
        >
          New order
        </button>
      </header>

      {actionErrorMessage && (
        <div className="error-card" role="alert">
          {actionErrorMessage}
        </div>
      )}

      {optionsErrorMessage && (
        <div className="error-card" role="alert">
          <strong>Unable to load order options.</strong>
          <p>{optionsErrorMessage}</p>
        </div>
      )}

      {isLoadingOrderDetail && <p>Loading order details...</p>}

      {isLoadingOrders && <p>Loading orders...</p>}

      {orderErrorMessage && (
        <div className="error-card" role="alert">
          <strong>Unable to load orders.</strong>
          <p>{orderErrorMessage}</p>
        </div>
      )}

      {!isLoadingOrders && !orderErrorMessage && orders.length === 0 && (
        <div className="empty-card">
          <strong>No orders found.</strong>
          <p>Orders created for the active scope will appear here.</p>
        </div>
      )}

      {!isLoadingOrders && !orderErrorMessage && orders.length > 0 && (
        <OrdersTable orders={orders} onSelectOrder={handleSelectOrder} />
      )}

      {selectedOrder && (
        <OrderActionsModal
          order={selectedOrder}
          onClose={() => setSelectedOrder(null)}
          onCancel={handleCancelOrder}
        />
      )}

      {isCreatingOrder && (
        <OrderFormModal
          stores={stores}
          vendors={vendors}
          defaultStoreId={defaultStoreId}
          requireStoreSelection={requireStoreSelection}
          onSubmit={handleCreateOrder}
          onClose={() => setIsCreatingOrder(false)}
        />
      )}
    </section>
  );
}