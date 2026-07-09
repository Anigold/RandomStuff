import { useEffect, useState, type ReactNode } from "react";
import { NavLink } from "react-router-dom";

import { navRoutes } from "../../app/routes";
import { StoreSelector } from "../../features/stores/components/StoreSelector";
import { useStoreScope } from "../../features/stores/hooks/useStoreScope";

const SIDEBAR_COLLAPSED_STORAGE_KEY = "workbot.sidebarCollapsed";

type AppLayoutProps = {
  children: ReactNode;
};

function readStoredSidebarCollapsed(): boolean {
  try {
    return window.localStorage.getItem(SIDEBAR_COLLAPSED_STORAGE_KEY) === "true";
  } catch {
    return false;
  }
}

function writeStoredSidebarCollapsed(isCollapsed: boolean): void {
  try {
    window.localStorage.setItem(
      SIDEBAR_COLLAPSED_STORAGE_KEY,
      String(isCollapsed),
    );
  } catch {
    // Ignore localStorage failures. React state will still work this session.
  }
}

function getRouteIcon(path: string, label: string): string {
  switch (path) {
    case "/":
      return "D";

    case "/items":
      return "I";

    case "/inventory":
      return "N";

    case "/orders":
      return "O";

    default:
      return label.slice(0, 1).toUpperCase();
  }
}



export function AppLayout({ children }: AppLayoutProps) {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(() =>
    readStoredSidebarCollapsed(),
  );

  useEffect(() => {
    writeStoredSidebarCollapsed(isSidebarCollapsed);
  }, [isSidebarCollapsed]);

  const shellClassName = isSidebarCollapsed
    ? "app-shell app-shell-collapsed"
    : "app-shell";



  const { activeScope } = useStoreScope();

  const visibleNavRoutes = navRoutes.filter((route) => {
    if (!route.requiredScopeType) {
      return true;
    }

    return activeScope?.type === route.requiredScopeType;
  });



  return (
    <div className={shellClassName}>
      <aside className="app-sidebar" aria-label="Primary navigation">
        <div className="app-sidebar-header">
          <div className="app-brand">
            <span className="app-brand-mark" aria-hidden="true">
              WB
            </span>

            <div className="app-brand-text">
              <h1>WorkBot</h1>
              <p>Operations Console</p>
            </div>
          </div>

          <button
            type="button"
            className="app-sidebar-toggle"
            aria-label={
              isSidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"
            }
            aria-expanded={!isSidebarCollapsed}
            onClick={() => setIsSidebarCollapsed((current) => !current)}
          >
            <span className="app-sidebar-toggle-icon" aria-hidden="true">
              ‹
            </span>
          </button>
        </div>

        <nav className="side-nav" aria-label="App sections">
          {visibleNavRoutes.map((route) => (
            <NavLink
              key={route.path}
              to={route.path}
              end={route.path === "/"}
              className={({ isActive }) =>
                isActive ? "side-nav-link active" : "side-nav-link"
              }
              title={isSidebarCollapsed ? route.label : undefined}
            >
              <span className="side-nav-link-icon" aria-hidden="true">
                {getRouteIcon(route.path, route.label)}
              </span>

              <span className="side-nav-link-label">{route.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="app-main">
        <header className="app-topbar">
          <StoreSelector />
        </header>

        <main className="app-content">{children}</main>
      </div>
    </div>
  );
}