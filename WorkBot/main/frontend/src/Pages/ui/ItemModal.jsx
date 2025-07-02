import React from 'react';
import Modal from '../ui/Modal';
import Button from '../ui/Button';

export default function ItemModal({ selectedItem, itemDetails, setItemDetails, onClose }) {
  if (!selectedItem) return null;

  return (
    <Modal onClose={onClose}>
      <h3 className="text-xl font-bold mb-4">Edit Item</h3>

      {!itemDetails ? (
        <p className="text-zinc-400 italic">Loading details...</p>
      ) : (
        <>
          <label className="block mb-4">
            <span className="block text-sm mb-1 text-zinc-300">Name:</span>
            <input
              type="text"
              value={itemDetails.item_name}
              onChange={(e) =>
                setItemDetails({ ...itemDetails, item_name: e.target.value })
              }
              className="w-full px-3 py-2 bg-zinc-800 border border-zinc-600 rounded text-white"
            />
          </label>

          <hr className="my-4 border-zinc-700" />

          <h4 className="text-lg font-semibold mb-2">Vendors</h4>
          <ul className="space-y-1 mb-4">
            {itemDetails.vendors.map((vendor, i) => (
              <li key={i} className="text-zinc-300">
                <span className="font-medium text-zinc-100">{vendor.vendor_name}</span> — SKU: <span className="text-zinc-400">{vendor.vendor_sku || 'N/A'}</span> — Price: <span className="text-green-400">${(vendor.price / 100).toFixed(2)}</span>
              </li>
            ))}
          </ul>

          <hr className="my-4 border-zinc-700" />

          <h4 className="text-lg font-semibold mb-2">Purchase History</h4>
          <div className="max-h-64 overflow-y-auto border border-zinc-700 rounded">
            <table className="w-full text-sm border border-zinc-700">
              <thead className="bg-zinc-800 text-zinc-300">
                <tr>
                  <th className="px-3 py-2 border-b border-zinc-700 text-left">Date</th>
                  <th className="px-3 py-2 border-b border-zinc-700 text-left">Store</th>
                  <th className="px-3 py-2 border-b border-zinc-700 text-left">Qty</th>
                  <th className="px-3 py-2 border-b border-zinc-700 text-left">Unit Cost</th>
                </tr>
              </thead>
              <tbody>
                {itemDetails.purchase_history.map((row, i) => (
                  <tr key={i} className="even:bg-zinc-800">
                    <td className="px-3 py-2">{row.date}</td>
                    <td className="px-3 py-2">{row.store}</td>
                    <td className="px-3 py-2">{row.quantity}</td>
                    <td className="px-3 py-2">${(row.cost_per / 100).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex justify-end gap-4 mt-6">
            <Button onClick={onClose} className="bg-zinc-700 hover:bg-zinc-600 text-white">
              Cancel
            </Button>
            <Button
              onClick={async () => {
                await fetch(`/api/items/${selectedItem.id}`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ item_name: itemDetails.item_name }),
                });
                onClose();
                window.location.reload();
              }}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              Save Changes
            </Button>
          </div>
        </>
      )}
    </Modal>
  );
}
