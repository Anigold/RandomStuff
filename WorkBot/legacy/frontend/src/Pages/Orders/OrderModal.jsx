import React from 'react';
import Modal from '../ui/Modal';
import Button from '../ui/Button';

export default function OrderModal({ order, onClose, onItemEdit }) {
  if (!order) return null;

  return (
    <Modal onClose={onClose}>
      <h3 className="text-xl font-bold mb-4">Order Summary</h3>
      <p className="text-zinc-200 mb-1">
        <strong>Store:</strong> {order.store_name}
      </p>
      <p className="text-zinc-200 mb-1">
        <strong>Vendor:</strong> {order.vendor_name}
      </p>
      <p className="text-zinc-200 mb-1">
        <strong>Date:</strong> {order.date}
      </p>
      <p className="text-zinc-200 mb-4">
        <strong>Total:</strong> ${(order.total_cost / 100).toFixed(2)}
      </p>

      {order.items && (
        <div className="mt-4">
          <h4 className="text-lg font-semibold text-white mb-2">Items</h4>
          <table className="w-full text-sm border border-zinc-700">
            <thead className="bg-zinc-800 text-zinc-300">
              <tr>
                <th className="px-3 py-2">Item</th>
                <th className="px-3 py-2">Qty</th>
                <th className="px-3 py-2">Unit Cost</th>
                <th className="px-3 py-2">Total</th>
              </tr>
            </thead>
            <tbody>
              {order.items.map((item, i) => (
                <tr
                  key={i}
                  onClick={() => onItemEdit(i)}
                  className="even:bg-zinc-800 hover:bg-zinc-700 cursor-pointer"
                >
                  <td className="px-3 py-2">{item.name}</td>
                  <td className="px-3 py-2">{item.quantity}</td>
                  <td className="px-3 py-2">${(item.cost_per / 100).toFixed(2)}</td>
                  <td className="px-3 py-2">${((item.cost_per * item.quantity) / 100).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="flex justify-end mt-6">
        <Button onClick={onClose} className="bg-blue-600 hover:bg-blue-700 text-white">
          Close
        </Button>
      </div>
    </Modal>
  );
}
