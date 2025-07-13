// src/Pages/Orders/Toolbar.jsx

import React from 'react';

export default function Toolbar({
  groupBy,
  setGroupBy,
  filters,
  setFilters,
  toggleAllGroups
}) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center gap-4 p-4 bg-zinc-800 rounded-lg shadow mb-6">
      {/* Group By */}
      <div className="flex items-center gap-2">
        <label className="text-sm text-zinc-300">Group by:</label>
        <select
          value={groupBy}
          onChange={(e) => setGroupBy(e.target.value)}
          className="px-2 py-1 bg-zinc-900 border border-zinc-600 text-white rounded"
        >
          <option value="">None</option>
          <option value="store">Store</option>
          <option value="vendor">Vendor</option>
        </select>
      </div>

      {/* Date Range */}
      <div className="flex items-center gap-2">
        <label className="text-sm text-zinc-300">Start:</label>
        <input
          type="date"
          value={filters.startDate}
          onChange={(e) =>
            setFilters((f) => ({ ...f, startDate: e.target.value }))
          }
          className="bg-zinc-900 border border-zinc-600 text-white px-2 py-1 rounded"
        />
        <label className="text-sm text-zinc-300">End:</label>
        <input
          type="date"
          value={filters.endDate}
          onChange={(e) =>
            setFilters((f) => ({ ...f, endDate: e.target.value }))
          }
          className="bg-zinc-900 border border-zinc-600 text-white px-2 py-1 rounded"
        />
      </div>

      {/* Placed Toggle */}
      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          checked={filters.hidePlaced}
          onChange={(e) =>
            setFilters((f) => ({ ...f, hidePlaced: e.target.checked }))
          }
          id="hidePlaced"
        />
        <label htmlFor="hidePlaced" className="text-sm text-zinc-300">
          Hide Placed
        </label>
      </div>

      {/* Expand/Collapse All */}
      <button
        onClick={toggleAllGroups}
        className="ml-auto bg-zinc-700 hover:bg-zinc-600 text-white px-3 py-1 text-sm rounded"
      >
        Toggle All Groups
      </button>
    </div>
  );
}
