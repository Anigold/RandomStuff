import React, { useEffect, useState, useMemo } from 'react';
import PageLayout from '../ui/PageLayout';
import Card from '../ui/Card';
import Modal from '../ui/Modal';
import Button from '../ui/Button';

export default function StoresPage() {
  const [stores, setStores] = useState([]);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('store_name');
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    fetch('/api/stores')
      .then(res => res.json())
      .then(setStores);
  }, []);

  const filtered = useMemo(() => {
    let result = [...stores];

    if (search.trim()) {
      const q = search.toLowerCase();
      result = result.filter(store =>
        store.store_name.toLowerCase().includes(q)
      );
    }

    result.sort((a, b) =>
      sortBy === 'store_name'
        ? a.store_name.localeCompare(b.store_name)
        : a.id - b.id
    );

    return result;
  }, [stores, search, sortBy]);

  return (
    <PageLayout>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold text-white">Stores</h2>
        <div className="flex gap-4">
          <input
            className="px-3 py-2 rounded bg-zinc-800 border border-zinc-600 text-white"
            placeholder="Search stores..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <select
            className="px-2 py-2 rounded bg-zinc-800 border border-zinc-600 text-white"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="store_name">Sort: Name</option>
            <option value="id">Sort: ID</option>
          </select>
        </div>
      </div>

      <div className="space-y-3">
        {filtered.map(store => (
          <Card
            key={store.id}
            onClick={() => setSelected(store)}
            className="w-full flex justify-between items-center"
          >
            <div>
              <h3 className="text-lg font-medium text-white">{store.store_name}</h3>
              <p className="text-sm text-zinc-400">{store.address}</p>
            </div>
            <div className="text-sm text-zinc-500 italic">Click to view</div>
          </Card>
        ))}
      </div>

      {selected && (
        <Modal onClose={() => setSelected(null)}>
          <h3 className="text-xl font-bold mb-4">Store Info</h3>
          <p className="mb-2 text-zinc-200"><strong>Name:</strong> {selected.store_name}</p>
          <p className="mb-4 text-zinc-200"><strong>Address:</strong> {selected.address}</p>
          <div className="flex justify-end">
            <Button onClick={() => setSelected(null)} className="bg-blue-600 hover:bg-blue-700 text-white">
              Close
            </Button>
          </div>
        </Modal>
      )}
    </PageLayout>
  );
}
