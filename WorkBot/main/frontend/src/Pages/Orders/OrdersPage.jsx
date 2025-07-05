import React, { useState, useEffect } from 'react';

import PageLayout from '../ui/PageLayout';
import OrderCard from './OrderCard';
import OrderModal from './OrderModal';
import EditOrderItemModal from './EditOrderItemModal';
import Toolbar from './Toolbar';


export default function OrdersPage() {
  const [orders, setOrders] = useState([]);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [editingItemIndex, setEditingItemIndex] = useState(null);

  useEffect(() => {
    fetch('/api/orders')
      .then(res => res.json())
      .then(setOrders);
  }, []);

  return (
    <PageLayout>
      <div className="flex gap-6">
        <div className="flex-1">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-semibold text-white">Orders</h2>
            {/* Collapse/Expand in toolbar */}
          </div>

          {/* Order list here */}
          <div className="space-y-4">
            {orders.map(order => (
              <OrderCard
                key={order.id}
                order={order}
                onClick={async () => {
                const summary = await fetch(`/api/orders/${order.id}`).then(res => res.json());
                const items = await fetch(`/api/orders/${order.id}/items`).then(res => res.json());
                setSelectedOrder({ ...summary, items });
                }}

              />
            ))}
          </div>
        </div>

        <Toolbar />
      </div>

      <OrderModal
        order={selectedOrder}
        onClose={() => {
          setSelectedOrder(null);
          setEditingItemIndex(null);
        }}
        onItemEdit={(index) => setEditingItemIndex(index)}
      />

      <EditOrderItemModal
        order={selectedOrder}
        index={editingItemIndex}
        onClose={() => setEditingItemIndex(null)}
        setOrder={setSelectedOrder}
      />
    </PageLayout>
  );
}
