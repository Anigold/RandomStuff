import { useEffect, useRef, useState } from "react";

import type { ItemDto } from "../../../api/itemsApi";
import { useVirtualRows } from "../../../shared/hooks/useVirtualRows";
import {
  getCountUnitLabel,
  getSortLabel,
  type ItemSortKey,
  type ItemSortState,
} from "../tableHelpers";

const ITEM_ROW_HEIGHT = 54;

type ItemsVirtualTableProps = {
  items: ItemDto[];
  sortState: ItemSortState;
  resetKey: string;
  onUpdateSort: (key: ItemSortKey) => void;
  onSelectItem: (item: ItemDto) => void;
};

export function ItemsVirtualTable({
  items,
  sortState,
  resetKey,
  onUpdateSort,
  onSelectItem,
}: ItemsVirtualTableProps) {
  const scrollContainerRef = useRef<HTMLDivElement | null>(null);

  const [scrollTop, setScrollTop] = useState(0);
  const [viewportHeight, setViewportHeight] = useState(0);

  function updateMeasurements() {
    const scrollContainer = scrollContainerRef.current;

    if (!scrollContainer) {
      return;
    }

    setScrollTop(scrollContainer.scrollTop);
    setViewportHeight(scrollContainer.clientHeight);
  }

  useEffect(() => {
    updateMeasurements();

    const scrollContainer = scrollContainerRef.current;

    if (!scrollContainer) {
      return;
    }

    if (!("ResizeObserver" in window)) {
      window.addEventListener("resize", updateMeasurements);

      return () => {
        window.removeEventListener("resize", updateMeasurements);
      };
    }

    const resizeObserver = new ResizeObserver(updateMeasurements);
    resizeObserver.observe(scrollContainer);

    return () => {
      resizeObserver.disconnect();
    };
  }, []);

  useEffect(() => {
    const scrollContainer = scrollContainerRef.current;

    if (!scrollContainer) {
      return;
    }

    scrollContainer.scrollTop = 0;
    setScrollTop(0);
  }, [resetKey]);

  const { virtualRows, totalHeight } = useVirtualRows({
    itemCount: items.length,
    rowHeight: ITEM_ROW_HEIGHT,
    scrollTop,
    viewportHeight,
    overscan: 10,
  });

  return (
    <div
      className="virtual-table"
      role="table"
      aria-rowcount={items.length}
      aria-label="Items"
    >
      <div className="virtual-table-header" role="row">
        <div className="virtual-table-header-cell" role="columnheader">
          <button
            type="button"
            className="table-sort-button"
            onClick={() => onUpdateSort("name")}
          >
            Name{getSortLabel("name", sortState)}
          </button>
        </div>

        <div className="virtual-table-header-cell" role="columnheader">
          <button
            type="button"
            className="table-sort-button"
            onClick={() => onUpdateSort("category")}
          >
            Category{getSortLabel("category", sortState)}
          </button>
        </div>

        <div className="virtual-table-header-cell" role="columnheader">
          <button
            type="button"
            className="table-sort-button"
            onClick={() => onUpdateSort("subcategory")}
          >
            Subcategory{getSortLabel("subcategory", sortState)}
          </button>
        </div>

        <div className="virtual-table-header-cell" role="columnheader">
          <button
            type="button"
            className="table-sort-button"
            onClick={() => onUpdateSort("countUnit")}
          >
            Count Unit{getSortLabel("countUnit", sortState)}
          </button>
        </div>

        <div className="virtual-table-header-cell" role="columnheader">
          <button
            type="button"
            className="table-sort-button"
            onClick={() => onUpdateSort("status")}
          >
            Status{getSortLabel("status", sortState)}
          </button>
        </div>
      </div>

      <div
        ref={scrollContainerRef}
        className="virtual-table-scroll"
        role="rowgroup"
        onScroll={updateMeasurements}
      >
        <div
          className="virtual-table-spacer"
          style={{ height: `${totalHeight}px` }}
        >
          {virtualRows.map((virtualRow) => {
            const item = items[virtualRow.index];

            if (!item) {
              return null;
            }

            return (
              <div
                key={item.id}
                className="virtual-table-row clickable-row"
                role="row"
                tabIndex={0}
                aria-rowindex={virtualRow.index + 1}
                style={{
                  height: `${virtualRow.size}px`,
                  transform: `translateY(${virtualRow.start}px)`,
                }}
                onClick={() => onSelectItem(item)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    onSelectItem(item);
                  }
                }}
              >
                <div className="virtual-table-cell" role="cell">
                  <strong>{item.name}</strong>
                </div>

                <div className="virtual-table-cell" role="cell">
                  {item.category ?? "—"}
                </div>

                <div className="virtual-table-cell" role="cell">
                  {item.subcategory ?? "—"}
                </div>

                <div className="virtual-table-cell" role="cell">
                  {getCountUnitLabel(item)}
                </div>

                <div className="virtual-table-cell" role="cell">
                  <span
                    className={
                      item.is_active
                        ? "status-badge status-badge-active"
                        : "status-badge status-badge-inactive"
                    }
                  >
                    {item.is_active ? "Active" : "Inactive"}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}