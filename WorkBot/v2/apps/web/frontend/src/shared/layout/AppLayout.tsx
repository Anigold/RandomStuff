import { NavLink } from "react-router-dom";
import type { ReactNode } from "react";

import { navRoutes } from "../../app/routes";
import { StoreSelector } from "../../features/stores/components/StoreSelector";

type AppLayoutProps = {
  children: ReactNode;
};

export function AppLayout({ children }: AppLayoutProps) {
  return (
    <div className="app-shell">
      <aside className="app-sidebar">
        <div className="app-brand">
          <span className="app-brand-mark">WB</span>

          <div>
            <h1>WorkBot</h1>
            <p>Operations Console</p>
          </div>
        </div>

        <nav className="side-nav">
          {navRoutes.map((route) => (
            <NavLink
              key={route.path}
              to={route.path}
              end={route.path === "/"}
              className={({ isActive }) =>
                isActive ? "side-nav-link active" : "side-nav-link"
              }
            >
              {route.label}
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