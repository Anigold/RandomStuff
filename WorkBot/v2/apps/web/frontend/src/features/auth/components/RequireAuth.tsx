import type { ReactNode } from "react";

import { useAuth } from "../hooks/useAuth";
import { LoginPage } from "../pages/LoginPage";

type RequireAuthProps = {
  children: ReactNode;
};

export function RequireAuth({ children }: RequireAuthProps) {
  const { status } = useAuth();

  if (status === "loading") {
    return (
      <main className="auth-loading">
        <p>Loading WorkBot...</p>
      </main>
    );
  }

  if (status === "unauthenticated") {
    return <LoginPage />;
  }

  return children;
}