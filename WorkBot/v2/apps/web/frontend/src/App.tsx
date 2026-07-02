import { appRoutes } from "./app/routes";
import { RequireAuth } from "./features/auth/components/RequireAuth";
import { StoreScopeProvider } from "./features/stores/StoreScopeProvider";
import { AppLayout } from "./shared/layout/AppLayout";

function getCurrentRoute() {
  const pathname = window.location.pathname;

  return appRoutes.find((route) => route.path === pathname) ?? appRoutes[0];
}

export default function App() {
  const route = getCurrentRoute();

  return (
    <RequireAuth>
      <StoreScopeProvider>
        <AppLayout>
          {route.element}
        </AppLayout>
      </StoreScopeProvider>
    </RequireAuth>
  );
}