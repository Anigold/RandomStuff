import type { ReactNode } from "react";

import { appRoutes } from "../../app/routes";
import { useAuth } from "../../features/auth/hooks/useAuth";
import { StoreSelector } from "../../features/stores/components/StoreSelector";

type AppLayoutProps = {
  children: ReactNode;
};

export function AppLayout({ children }: AppLayoutProps) {
  const { currentUser, logout } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <div>
            <h1>WorkBot</h1>

            <StoreSelector />

            <nav>
              {appRoutes.map((route) => (
                <a key={route.path} href={route.path}>
                  {route.label}
                </a>
              ))}
            </nav>
          </div>
        </div>

        <div className="sidebar-user">
          {currentUser && (
            <p>
              Signed in as{" "}
              <strong>
                {currentUser.display_name ?? currentUser.username}
              </strong>
            </p>
          )}

          <button type="button" onClick={() => void logout()}>
            Sign out
          </button>
        </div>
      </aside>

      <main className="main-content">{children}</main>
    </div>
  );
}