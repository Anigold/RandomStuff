import { Navigate, Route, Routes } from "react-router-dom";

import App from "../App";
import { ItemsListPage } from "../features/items/pages/ItemsListPage";
import { InventoryPage } from "../features/inventory/pages/InventoryPage";

function DashboardPage() {
  return (
    <section>
      <h2>Dashboard</h2>
      <p>You are signed in.</p>
    </section>
  );
}

function OrdersPage() {
  return (
    <section>
      <h2>Orders</h2>
      <p>Orders will be ported after items.</p>
    </section>
  );
}

function NotFoundPage() {
  return (
    <section>
      <h2>Page not found</h2>
      <p>The requested page does not exist.</p>
    </section>
  );
}

export const navRoutes = [
  { path: "/", label: "Dashboard" },
  { path: "/items", label: "Items" },
  { path: "/inventory", label: "Inventory" },
  { path: "/orders", label: "Orders" },
];

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<App />}>
        <Route index element={<DashboardPage />} />
        <Route path="items" element={<ItemsListPage />} />
        <Route path="inventory" element={<InventoryPage />} />
        <Route path="orders" element={<OrdersPage />} />
        <Route path="404" element={<NotFoundPage />} />
        <Route path="*" element={<Navigate to="/404" replace />} />
      </Route>
    </Routes>
  );
}