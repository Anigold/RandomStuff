import React, { useEffect, useState } from 'react';
import PageLayout from '../ui/PageLayout';
import Card from '../ui/Card';
import ItemModal from '../ui/ItemModal';

export default function ItemsPage() {
  const [items, setItems] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [itemDetails, setItemDetails] = useState(null);

  // Fetch all items on load
  useEffect(() => {
    fetch('/api/items')
      .then((res) => res.json())
      .then((data) => setItems(data));
  }, []);

  // Fetch item details when selected
  useEffect(() => {
    if (!selectedItem) return;
  
    console.log("🧪 Fetching item details for ID:", selectedItem.id);
  
    fetch(`/api/items/${selectedItem.id}/details`)
      .then(async (res) => {
        const text = await res.text();
        console.log("📦 Raw response from /api/items/:id →", text);
        return JSON.parse(text);
      })
      .then((data) => setItemDetails(data))
      .catch((err) => {
        console.error("❌ JSON parse or fetch error:", err);
      });
  }, [selectedItem]);
  

  const closeModal = () => {
    setSelectedItem(null);
    setItemDetails(null);
  };

  return (
    <PageLayout>
      <h2 className="text-2xl font-semibold text-white mb-4">Items</h2>
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        {items.map((item) => (
          <Card key={item.id} onClick={() => setSelectedItem(item)}>
            <h3 className="text-lg font-medium text-white">{item.name}</h3>
            <p className="text-sm text-zinc-400">ID: {item.id}</p>
          </Card>
        ))}
      </div>

      {/* Modal */}
      <ItemModal
        selectedItem={selectedItem}
        itemDetails={itemDetails}
        setItemDetails={setItemDetails}
        onClose={closeModal}
      />
    </PageLayout>
  );
}
