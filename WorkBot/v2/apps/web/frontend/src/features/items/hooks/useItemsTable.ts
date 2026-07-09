import { useCallback, useEffect, useMemo, useState } from "react";

import type { ItemDto } from "../../../api/itemsApi";
import {
  getSearchText,
  getUniqueSortedValues,
  normalize,
  sortItems,
  type ItemSortKey,
  type ItemSortState,
  type ItemStatusFilter,
} from "../tableHelpers";

type UseItemsTableResult = {
  categories: string[];
  visibleItems: ItemDto[];
  searchText: string;
  categoryFilter: string;
  statusFilter: ItemStatusFilter;
  sortState: ItemSortState;
  resetKey: string;
  setSearchText: (value: string) => void;
  setCategoryFilter: (value: string) => void;
  setStatusFilter: (value: ItemStatusFilter) => void;
  updateSort: (key: ItemSortKey) => void;
  clearFilters: () => void;
};

export function useItemsTable(items: ItemDto[]): UseItemsTableResult {
  const [searchText, setSearchTextState] = useState("");
  const [categoryFilter, setCategoryFilterState] = useState("");
  const [statusFilter, setStatusFilterState] =
    useState<ItemStatusFilter>("all");
  const [sortState, setSortState] = useState<ItemSortState>({
    key: "name",
    direction: "asc",
  });

  const categories = useMemo(
    () => getUniqueSortedValues(items, (item) => item.category),
    [items],
  );

  useEffect(() => {
    if (categoryFilter && !categories.includes(categoryFilter)) {
      setCategoryFilterState("");
    }
  }, [categories, categoryFilter]);

  const visibleItems = useMemo(() => {
    const normalizedSearchText = normalize(searchText);

    const filteredItems = items.filter((item) => {
      const matchesSearch =
        normalizedSearchText === "" ||
        getSearchText(item).includes(normalizedSearchText);

      const matchesCategory =
        categoryFilter === "" || item.category === categoryFilter;

      const matchesStatus =
        statusFilter === "all" ||
        (statusFilter === "active" && item.is_active) ||
        (statusFilter === "inactive" && !item.is_active);

      return matchesSearch && matchesCategory && matchesStatus;
    });

    return sortItems(filteredItems, sortState);
  }, [items, searchText, categoryFilter, statusFilter, sortState]);

  const setSearchText = useCallback((value: string) => {
    setSearchTextState(value);
  }, []);

  const setCategoryFilter = useCallback((value: string) => {
    setCategoryFilterState(value);
  }, []);

  const setStatusFilter = useCallback((value: ItemStatusFilter) => {
    setStatusFilterState(value);
  }, []);

  const updateSort = useCallback((key: ItemSortKey) => {
    setSortState((current) => {
      if (current.key !== key) {
        return {
          key,
          direction: "asc",
        };
      }

      return {
        key,
        direction: current.direction === "asc" ? "desc" : "asc",
      };
    });
  }, []);

  const clearFilters = useCallback(() => {
    setSearchTextState("");
    setCategoryFilterState("");
    setStatusFilterState("all");
  }, []);

  const resetKey = useMemo(
    () =>
      [
        items.length,
        searchText,
        categoryFilter,
        statusFilter,
        sortState.key,
        sortState.direction,
      ].join("|"),
    [
      items.length,
      searchText,
      categoryFilter,
      statusFilter,
      sortState.key,
      sortState.direction,
    ],
  );

  return {
    categories,
    visibleItems,
    searchText,
    categoryFilter,
    statusFilter,
    sortState,
    resetKey,
    setSearchText,
    setCategoryFilter,
    setStatusFilter,
    updateSort,
    clearFilters,
  };
}