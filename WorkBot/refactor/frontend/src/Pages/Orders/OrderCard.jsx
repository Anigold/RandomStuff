import React from 'react';
import Card from '../ui/Card';

export default function OrderCard({ order, onClick }) {
  return (
    <Card
      className={`w-full cursor-pointer hover:bg-zinc-700 ${
        order.placed ? 'opacity-60' : ''
      }`}
      onClick={onClick}
    >
      <h4 className="text-md text-white font-medium">
        {order.store_name} → {order.vendor_name}
      </h4>
      <p className="text-sm text-zinc-400">Date: {order.date}</p>
      <p className="text-sm text-zinc-400">
        {order.item_count} items — ${(order.total_cost / 100).toFixed(2)}
      </p>
    </Card>
  );
}
