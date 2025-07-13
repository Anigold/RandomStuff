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

  const [groupBy, setGroupBy] = useState('');
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    hidePlaced: false,
  });

  const [expandedGroups, setExpandedGroups] = useState({});

  useEffect(() => {
    fetch('/api/orders')
      .then((res) => res.json())
      .then((data) => {
        setOrders(data);

        const initialGroups = {};
        data.forEach((order) => {
          const key =
            groupBy === 'vendor'
              ? order.vendor_name
              : groupBy === 'store'
              ? order.store_name
              : 'all';
          if (!(key in initialGroups)) initialGroups[key] = true;
        });
        setExpandedGroups(initialGroups);
      });
  }, []);

  const toggleAllGroups = () => {
    const allKeys = new Set();
    filteredOrders.forEach(order => {
      const key =
        groupBy === 'vendor'
          ? order.vendor_name
          : groupBy === 'store'
          ? order.store_name
          : 'all';
      allKeys.add(key);
    });
  
    const allExpanded = Array.from(allKeys).every(k => expandedGroups[k]);
    const newState = {};
    allKeys.forEach(key => {
      newState[key] = !allExpanded;
    });
  
    setExpandedGroups(prev => ({ ...prev, ...newState }));
  };
  
  const filteredOrders = orders.filter((order) => {
    if (filters.hidePlaced && order.placed) return false;
    if (filters.startDate && order.date < filters.startDate) return false;
    if (filters.endDate && order.date > filters.endDate) return false;
    return true;
  });

  const grouped = {};
  filteredOrders.forEach((order) => {
    const key =
      groupBy === 'vendor'
        ? order.vendor_name
        : groupBy === 'store'
        ? order.store_name
        : 'all';
    if (!grouped[key]) grouped[key] = [];
    grouped[key].push(order);
  });

  return (
    <PageLayout>
      <div className="flex gap-6">
        <div className="flex-1">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-semibold text-white">Orders</h2>
          </div>

          <Toolbar
            groupBy={groupBy}
            setGroupBy={setGroupBy}
            filters={filters}
            setFilters={setFilters}
            toggleAllGroups={toggleAllGroups}
          />

          <div className="space-y-6">
            {Object.entries(grouped).map(([groupKey, orders]) => (
              <div key={groupKey}>
                {groupBy && (
                  <button
                    onClick={() =>
                      setExpandedGroups((prev) => ({
                        ...prev,
                        [groupKey]: !prev[groupKey],
                      }))
                    }
                    className="text-left w-full text-white font-semibold py-2 px-3 bg-zinc-700 rounded hover:bg-zinc-600 mb-2"
                  >
                    {expandedGroups[groupKey] ? '▼' : '▶'} {groupKey}
                  </button>
                )}
                {(!groupBy || expandedGroups[groupKey]) && (
                  <div className="space-y-4">
                    {orders.map((order) => (
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
                )}
              </div>
            ))}
          </div>
        </div>
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
