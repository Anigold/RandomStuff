import { useStoreScope } from "../hooks/useStoreScope";

export function StoreSelector() {
  const {
    scopes,
    activeScopeId,
    isLoadingScopes,
    scopeErrorMessage,
    setActiveScopeId,
  } = useStoreScope();

  if (isLoadingScopes) {
    return <p className="sidebar-muted">Loading scopes...</p>;
  }

  if (scopeErrorMessage) {
    return <p className="sidebar-error">Unable to load scopes.</p>;
  }

  if (scopes.length === 0) {
    return <p className="sidebar-muted">No scopes available.</p>;
  }

  return (
    <label className="store-selector">
      Operating Scope
      <select
        value={activeScopeId ?? ""}
        onChange={(event) => setActiveScopeId(event.target.value)}
      >
        {scopes.map((scope) => (
          <option key={scope.id} value={scope.id}>
            {scope.type === "supervisor"
              ? `${scope.name} — All Stores`
              : scope.name}
          </option>
        ))}
      </select>
    </label>
  );
}