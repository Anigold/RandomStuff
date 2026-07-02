import type { ReactNode } from "react";

import { ItemsListPage } from "../features/items/pages/ItemsListPage";

type AppRoute = {
  path: string;
  label: string;
  element: ReactNode;
};

export const appRoutes: AppRoute[] = [
  {path: "/", label: "Dashboard",
    element: (
      <section>
        <h2>Dashboard</h2>
        <p>You are signed in.</p>
      </section>
    ),
  },
  {path: "/items", label: "Items", 
    element: <ItemsListPage />,
  },
  {path: "/orders", label: "Orders",
    element: (
      <section>
        <h2>Orders</h2>
        <p>Orders will be ported after items.</p>
      </section>
    ),
  },
];