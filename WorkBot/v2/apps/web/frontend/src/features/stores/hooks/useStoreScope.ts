import { useContext } from "react";

import { StoreScopeContext } from "../StoreScopeProvider";

export function useStoreScope() {
  const value = useContext(StoreScopeContext);

  if (!value) {
    throw new Error("useStoreScope must be used within StoreScopeProvider");
  }

  return value;
}