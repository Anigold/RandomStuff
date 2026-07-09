import { useMemo } from "react";

export type VirtualRow = {
  index: number;
  start: number;
  size: number;
  end: number;
};

type UseVirtualRowsArgs = {
  itemCount: number;
  rowHeight: number;
  scrollTop: number;
  viewportHeight: number;
  overscan?: number;
};

type UseVirtualRowsResult = {
  virtualRows: VirtualRow[];
  totalHeight: number;
};

export function useVirtualRows({
  itemCount,
  rowHeight,
  scrollTop,
  viewportHeight,
  overscan = 8,
}: UseVirtualRowsArgs): UseVirtualRowsResult {
  const safeItemCount = Math.max(0, itemCount);
  const totalHeight = safeItemCount * rowHeight;

  const virtualRows = useMemo(() => {
    if (safeItemCount === 0 || rowHeight <= 0 || viewportHeight <= 0) {
      return [];
    }

    const startIndex = Math.max(
      0,
      Math.floor(scrollTop / rowHeight) - overscan,
    );

    const endIndex = Math.min(
      safeItemCount - 1,
      Math.ceil((scrollTop + viewportHeight) / rowHeight) + overscan,
    );

    const rows: VirtualRow[] = [];

    for (let index = startIndex; index <= endIndex; index += 1) {
      const start = index * rowHeight;

      rows.push({
        index,
        start,
        size: rowHeight,
        end: start + rowHeight,
      });
    }

    return rows;
  }, [safeItemCount, rowHeight, scrollTop, viewportHeight, overscan]);

  return {
    virtualRows,
    totalHeight,
  };
}