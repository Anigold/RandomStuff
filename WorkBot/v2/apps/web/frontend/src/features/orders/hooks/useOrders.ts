import { useCallback, useEffect, useState } from "react";

import { listOrders, type OrderDto } from "../../../api/ordersApi";
import { useAccessToken } from "../../auth/hooks/useAccessTokens";
import { useStoreScope } from "../../stores/hooks/useStoreScope";

type UseOrdersResult = {
  orders: OrderDto[];
  isLoadingOrders: boolean;
  orderErrorMessage: string | null;
  reloadOrders: () => Promise<void>;
};

export function useOrders(): UseOrdersResult {
  const accessToken = useAccessToken();
  const { activeScopeId, isLoadingScopes } = useStoreScope();

  const [orders, setOrders] = useState<OrderDto[]>([]);
  const [isLoadingOrders, setIsLoadingOrders] = useState(true);
  const [orderErrorMessage, setOrderErrorMessage] = useState<string | null>(
    null,
  );

  const reloadOrders = useCallback(async () => {
    if (isLoadingScopes) {
      return;
    }

    if (!activeScopeId) {
      setOrders([]);
      setIsLoadingOrders(false);
      setOrderErrorMessage("Select an operating scope before loading orders.");
      return;
    }

    setIsLoadingOrders(true);
    setOrderErrorMessage(null);

    try {
      const loadedOrders = await listOrders({
        accessToken,
        scopeId: activeScopeId,
      });

      setOrders(loadedOrders);
    } catch (error) {
      setOrderErrorMessage(
        error instanceof Error ? error.message : "Unable to load orders.",
      );
    } finally {
      setIsLoadingOrders(false);
    }
  }, [accessToken, activeScopeId, isLoadingScopes]);

  useEffect(() => {
    void reloadOrders();
  }, [reloadOrders]);

  return {
    orders,
    isLoadingOrders,
    orderErrorMessage,
    reloadOrders,
  };
}