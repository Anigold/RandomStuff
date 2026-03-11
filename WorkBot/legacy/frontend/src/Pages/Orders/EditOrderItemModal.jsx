import {useEffect, useState, React} from 'react';
import Modal from '../ui/Modal';
import Button from '../ui/Button';

export default function EditOrderItemModal({ order, index, onClose, setOrder }) {

  const [vendorItems, setVendorItems] = useState([]);

  useEffect(() => {
    if (!order?.vendor_id) return;
    fetch(`/api/vendors/${order.vendor_id}/items`)
    .then(res => res.json())
    .then(data => {
      console.log("Vendor items:", data); // 🔍 Check
      setVendorItems(data);
    });
  }, [order]);

  if (!order || index === null) return null; // ✅ Only after hooks

  const item = order.items[index];


  return (
    <Modal onClose={onClose}>
      <h3 className="text-lg font-bold mb-4">Edit Item</h3>
      <div className="space-y-4">
        <div>
          <label className="block text-sm text-zinc-300 mb-1">Item Name</label>
          <div className="px-3 py-2 bg-zinc-800 border border-zinc-600 rounded text-white">
            {item.name}
          </div>
        </div>

        <div>
          <label className="block text-sm text-zinc-300 mb-1">Quantity</label>
          <input
            type="number"
            value={item.quantity}
            onChange={(e) => {
              const updated = [...order.items];
              updated[index].quantity = parseInt(e.target.value);
              setOrder({ ...order, items: updated });
            }}
            className="w-full px-3 py-2 bg-zinc-800 border border-zinc-600 rounded text-white"
          />
        </div>

        <div>
          <label className="block text-sm text-zinc-300 mb-1">Vendor SKU / Price</label>
          <select
            className="w-full px-3 py-2 bg-zinc-800 border border-zinc-600 rounded text-white"
            value={item.vendor_sku || ""}
            onChange={(e) => {
              const selected = vendorItems.find(v => v.sku === e.target.value);
              const updated = [...order.items];
              updated[index] = {
                ...updated[index],
                name: selected.name,
                cost_per: selected.price,
                vendor_sku: selected.sku
              };
              setOrder({ ...order, items: updated });
            }}
          >
            <option value="">Select a vendor SKU</option>
            {vendorItems.map((vi, i) => (
              <option key={i} value={vi.sku}>
                {vi.name} — SKU: {vi.sku || "N/A"} — ${(vi.price / 100).toFixed(2)}
              </option>
            ))}
          </select>
        </div>


        <div className="flex justify-end pt-4">
          <Button onClick={onClose} className="bg-zinc-700 hover:bg-zinc-600 text-white">
            Close
          </Button>
        </div>
      </div>
    </Modal>
  );
}
