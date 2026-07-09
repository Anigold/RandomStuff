import type { ItemDto } from "../../../api/itemsApi";
import { useItemsTable } from "../hooks/useItemsTable";
import { ItemsTableToolbar } from "./ItemsTableToolbar";
import { ItemsVirtualTable } from "./ItemsVirtualTable";

type ItemsTableProps = {
  items: ItemDto[];
  onSelectItem: (item: ItemDto) => void;
};

export function ItemsTable({ items, onSelectItem }: ItemsTableProps) {
  const {
    categories,
    visibleItems,
    categoryFilter,
    statusFilter,
    sortState,
    resetKey,
    setSearchText,
    setCategoryFilter,
    setStatusFilter,
    updateSort,
    clearFilters,
  } = useItemsTable(items);

  return (
    <div className="table-card virtual-table-card">
      <ItemsTableToolbar
        categories={categories}
        itemCount={items.length}
        visibleItemCount={visibleItems.length}
        categoryFilter={categoryFilter}
        statusFilter={statusFilter}
        onSearchTextChange={setSearchText}
        onCategoryFilterChange={setCategoryFilter}
        onStatusFilterChange={setStatusFilter}
        onClearFilters={clearFilters}
      />

      {visibleItems.length === 0 ? (
        <div className="empty-card">
          <strong>No matching items found.</strong>
          <p>Try changing your search or filters.</p>
        </div>
      ) : (
        <ItemsVirtualTable
          items={visibleItems}
          sortState={sortState}
          resetKey={resetKey}
          onUpdateSort={updateSort}
          onSelectItem={onSelectItem}
        />
      )}
    </div>
  );
}