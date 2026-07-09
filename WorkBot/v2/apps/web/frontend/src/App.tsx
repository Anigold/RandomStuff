import { Outlet } from "react-router-dom";

import { RequireAuth } from "./features/auth/components/RequireAuth";
import { StoreScopeProvider } from "./features/stores/StoreScopeProvider";
import { AppLayout } from "./shared/layout/AppLayout";

export default function App() {
  return (
    <RequireAuth>
      <StoreScopeProvider>
        <AppLayout>
          <Outlet />
        </AppLayout>
      </StoreScopeProvider>
    </RequireAuth>
  );
}