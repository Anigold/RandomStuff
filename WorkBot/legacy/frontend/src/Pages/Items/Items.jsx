import React, { useEffect, useState, useMemo } from 'react';
import PageLayout from '../ui/PageLayout';
import Card from '../ui/Card';
import ItemModal from './ItemModal';

export default function ItemsPage() {
  const [items, setItems] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [itemDetails, setItemDetails] = useState(null);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('item_name'); // or 'id'

  useEffect(() => {
    fetch('/api/items')
      .then((res) => res.json())
      .then((data) => setItems(data));
  }, []);

  const filtered = useMemo(() => {
    let result = [...items];

    if (search.trim()) {
      const query = search.toLowerCase();
      result = result.filter((item) =>
        item.item_name.toLowerCase().includes(query)
      );
    }

    result.sort((a, b) => {
      if (sortBy === 'item_name') {
        return (a.item_name || '').localeCompare(b.item_name || '');
      } else {
        return (a.id || 0) - (b.id || 0);
      }
    });

    return result;
  }, [items, search, sortBy]);

  useEffect(() => {
    if (!selectedItem) return;
    fetch(`/api/items/${selectedItem.id}/details`)
      .then((res) => res.json())
      .then((data) => setItemDetails(data));
  }, [selectedItem]);

  const closeModal = () => {
    setSelectedItem(null);
    setItemDetails(null);
  };

  return (
    <PageLayout>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold text-white">Items</h2>
        <div className="flex gap-4">
          <input
            type="text"
            placeholder="Search items..."
            className="px-3 py-2 rounded bg-zinc-800 border border-zinc-600 text-white"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <select
            className="px-2 py-2 rounded bg-zinc-800 border border-zinc-600 text-white"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="item_name">Sort: Name</option>
            <option value="id">Sort: ID</option>
          </select>
        </div>
      </div>

      <div className="space-y-3">
        {filtered.map((item) => (
          <Card
            key={item.id}
            onClick={() => setSelectedItem(item)}
            className="w-full flex justify-between items-center"
          >
            <div>
              <h3 className="text-lg font-medium text-white">{item.item_name}</h3>
              <p className="text-sm text-zinc-400">ID: {item.id}</p>
            </div>
            <div className="text-sm text-zinc-500 italic">Click to edit</div>
          </Card>
        ))}
      </div>

      <ItemModal
        selectedItem={selectedItem}
        itemDetails={itemDetails}
        setItemDetails={setItemDetails}
        onClose={closeModal}
      />
    </PageLayout>
  );
}
