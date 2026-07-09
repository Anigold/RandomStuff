import { useEffect, useState } from "react";

import { useDebouncedValue } from "../../../shared/hooks/useDebouncedValue";
import type { ItemStatusFilter } from "../tableHelpers";

type ItemsTableToolbarProps = {
  categories: string[];
  itemCount: number;
  visibleItemCount: number;
  categoryFilter: string;
  statusFilter: ItemStatusFilter;
  onSearchTextChange: (value: string) => void;
  onCategoryFilterChange: (value: string) => void;
  onStatusFilterChange: (value: ItemStatusFilter) => void;
  onClearFilters: () => void;
};

export function ItemsTableToolbar({
  categories,
  itemCount,
  visibleItemCount,
  categoryFilter,
  statusFilter,
  onSearchTextChange,
  onCategoryFilterChange,
  onStatusFilterChange,
  onClearFilters,
}: ItemsTableToolbarProps) {
  const [liveSearchText, setLiveSearchText] = useState("");
  const debouncedSearchText = useDebouncedValue(liveSearchText, 250);

  const hasActiveFilters =
    liveSearchText.trim() !== "" ||
    categoryFilter !== "" ||
    statusFilter !== "all";

  const isSearchPending = liveSearchText !== debouncedSearchText;

  useEffect(() => {
    onSearchTextChange(debouncedSearchText);
  }, [debouncedSearchText, onSearchTextChange]);

  function handleClearFilters() {
    setLiveSearchText("");
    onSearchTextChange("");
    onClearFilters();
  }

  return (
    <div className="table-toolbar">
      <div className="table-toolbar-main">
        <div className="table-search-box">
          <span className="table-search-icon" aria-hidden="true">
            ⌕
          </span>

          <input
            type="search"
            aria-label="Search items"
            value={liveSearchText}
            onChange={(event) => setLiveSearchText(event.target.value)}
            placeholder="Search items..."
          />
        </div>

        <div className="table-result-summary">
          {isSearchPending
            ? "Searching..."
            : `Showing ${visibleItemCount} of ${itemCount}`}
        </div>
      </div>

      <div className="table-filter-row">
        <label className="table-filter-control">
          <span>Category</span>
          <select
            value={categoryFilter}
            onChange={(event) => onCategoryFilterChange(event.target.value)}
          >
            <option value="">All</option>

            {categories.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </label>

        <label className="table-filter-control">
          <span>Status</span>
          <select
            value={statusFilter}
            onChange={(event) =>
              onStatusFilterChange(event.target.value as ItemStatusFilter)
            }
          >
            <option value="all">All</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </label>

        {hasActiveFilters && (
          <button
            type="button"
            className="table-clear-button"
            onClick={handleClearFilters}
          >
            Clear
          </button>
        )}
      </div>
    </div>
  );
}